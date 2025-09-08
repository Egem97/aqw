from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional
import asyncpg
import asyncio
from datetime import datetime
from contextlib import asynccontextmanager
import logging
from config import settings
from cache_manager import cache_manager, cached

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
pool: Optional[asyncpg.Pool] = None

# Pydantic models
class FolderRequest(BaseModel):
    folder_name: str

class ImageResponse(BaseModel):
    id: int
    folder_id: str
    folder_name: str
    folder_webviewlink: str
    folder_modifiedtime: datetime
    image_id: str
    image_name: str
    image_webviewlink: str
    image_modifiedtime: datetime
    image_base64: str
    image_size_mb: float
    created_at: datetime

# Pydantic models for Presentaciones
class PresentacionBase(BaseModel):
    descripcion_producto: str
    peso_caja: float
    sobre_peso: float
    esquinero_adicionales: int

class PresentacionCreate(PresentacionBase):
    pass

class PresentacionUpdate(BaseModel):
    descripcion_producto: Optional[str] = None
    peso_caja: Optional[float] = None
    sobre_peso: Optional[float] = None
    esquinero_adicionales: Optional[int] = None

class PresentacionResponse(PresentacionBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Pydantic models for phl_pt_all_tabla
class PhlPtAllTablaBase(BaseModel):
    envio: Optional[str] = None
    semana: Optional[float] = None
    fecha_produccion: Optional[datetime] = None
    fecha_cosecha: Optional[datetime] = None
    cliente: Optional[str] = None
    tipo_pallet: Optional[str] = None
    contenedor: Optional[str] = None
    descripcion_producto: Optional[str] = None
    destino: Optional[str] = None
    fundo: Optional[str] = None
    variedad: Optional[str] = None
    n_cajas: Optional[float] = None
    n_pallet: Optional[str] = None
    turno: Optional[float] = None
    linea: Optional[float] = None
    phl_origen: Optional[str] = None
    materiales_adicionales: Optional[str] = None
    observaciones: Optional[str] = None
    sobre_peso: Optional[int] = None
    peso_caja: Optional[float] = None
    exportable: Optional[float] = None
    estado: Optional[str] = None

class PhlPtAllTablaResponse(PhlPtAllTablaBase):
    id: int
    created_at: datetime
    updated_at: datetime

# Database connection pool management
async def create_db_pool():
    """Create database connection pool"""
    global pool
    try:
        pool = await asyncpg.create_pool(
            host=settings.db_host,
            port=settings.db_port,
            database=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            min_size=settings.db_min_connections,
            max_size=settings.db_max_connections,
            command_timeout=60,
            server_settings={
                'jit': 'off'  # Disable JIT for better connection performance
            }
        )
        logger.info(f"Database pool created successfully with {settings.db_min_connections}-{settings.db_max_connections} connections")
    except Exception as e:
        logger.error(f"Failed to create database pool: {e}")
        raise

async def close_db_pool():
    """Close database connection pool"""
    global pool
    if pool:
        await pool.close()
        logger.info("Database pool closed")

# Lifespan context manager for FastAPI
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await create_db_pool()
    await cache_manager.initialize()
    yield
    # Shutdown
    await close_db_pool()
    await cache_manager.close()

# Initialize FastAPI app with lifespan
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan
)

# Dependency to get database connection from pool
async def get_db_connection():
    """Get database connection from pool"""
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not initialized")
    
    try:
        async with pool.acquire() as connection:
            yield connection
    except Exception as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=500, detail=f"Database connection error: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "API REST para consultar imágenes por folder_name",
        "version": settings.api_version,
        "port": settings.port,
        "async_optimized": True
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    """Async health check with database connection test"""
    try:
        if not pool:
            return {
                "status": "unhealthy", 
                "database": "pool_not_initialized",
                "port": settings.port
            }
        
        async with pool.acquire() as connection:
            # Test query
            result = await connection.fetchval("SELECT 1")
            
            # Pool statistics
            pool_stats = {
                "size": pool.get_size(),
                "idle": pool.get_idle_size(),
                "min_size": pool.get_min_size(),
                "max_size": pool.get_max_size()
            }
            
            # Cache statistics
            cache_stats = await cache_manager.get_stats()
            
            return {
                "status": "healthy",
                "database": "connected",
                "port": settings.port,
                "pool_stats": pool_stats,
                "cache_stats": cache_stats,
                "test_query": result
            }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "database": "error",
            "port": settings.port,
            "error": str(e)
        }

# Optimized POST endpoint to get images by folder_name with cache
@app.post("/images/by-folder", response_model=List[ImageResponse])
async def get_images_by_folder(
    request: FolderRequest,
    use_cache: bool = Query(True, description="Usar cache para la respuesta")
):
    """
    Obtiene todas las imágenes filtradas por folder_name (Optimizado con cache)
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    # Generar clave de cache
    cache_key = cache_manager._generate_cache_key(
        "images_by_folder",
        folder_name=request.folder_name
    )
    
    try:
        # Intentar obtener del cache si está habilitado
        if use_cache and settings.cache_enabled:
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for folder: {request.folder_name}")
                # Convertir dict a ImageResponse objects
                images = [ImageResponse(**item) for item in cached_result]
                return images
        
        async with pool.acquire() as connection:
            # Optimized SQL query with proper indexing hint
            query = """
            SELECT 
                id,
                folder_id,
                folder_name,
                folder_webviewlink,
                folder_modifiedtime,
                image_id,
                image_name,
                image_webviewlink,
                image_modifiedtime,
                image_base64,
                image_size_mb,
                created_at
            FROM images_fcl_drive
            WHERE folder_name = $1
            ORDER BY created_at DESC
            """
            
            # Execute async query
            rows = await connection.fetch(query, request.folder_name)
            
            if not rows:
                raise HTTPException(
                    status_code=404,
                    detail=f"No se encontraron imágenes para el folder_name: {request.folder_name}"
                )
            
            # Convert rows to response models efficiently
            images = [
                ImageResponse(
                    id=row['id'],
                    folder_id=row['folder_id'],
                    folder_name=row['folder_name'],
                    folder_webviewlink=row['folder_webviewlink'],
                    folder_modifiedtime=row['folder_modifiedtime'],
                    image_id=row['image_id'],
                    image_name=row['image_name'],
                    image_webviewlink=row['image_webviewlink'],
                    image_modifiedtime=row['image_modifiedtime'],
                    image_base64=row['image_base64'],
                    image_size_mb=row['image_size_mb'],
                    created_at=row['created_at']
                )
                for row in rows
            ]
            
            # Guardar en cache si está habilitado
            if use_cache and settings.cache_enabled:
                # Convertir a dict para serializar
                cache_data = [img.model_dump() for img in images]
                await cache_manager.set(cache_key, cache_data)
                logger.info(f"Cached {len(images)} images for folder: {request.folder_name}")
            
            logger.info(f"Successfully retrieved {len(images)} images for folder: {request.folder_name}")
            return images
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving images for folder {request.folder_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Optimized endpoint to get all unique folder names with cache
@app.get("/folders", response_model=List[str])
async def get_all_folders(use_cache: bool = Query(True, description="Usar cache para la respuesta")):
    """
    Obtiene todos los folder_name únicos disponibles (Optimizado con cache)
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    # Generar clave de cache
    cache_key = "folders_list"
    
    try:
        # Intentar obtener del cache si está habilitado
        if use_cache and settings.cache_enabled:
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info("Cache hit for folders list")
                return cached_result
        
        async with pool.acquire() as connection:
            # Optimized query for distinct folder names
            query = """
            SELECT DISTINCT folder_name 
            FROM images_fcl_drive 
            WHERE folder_name IS NOT NULL
            ORDER BY folder_name
            """
            
            rows = await connection.fetch(query)
            folder_names = [row['folder_name'] for row in rows]
            
            # Guardar en cache si está habilitado (TTL más largo para folders)
            if use_cache and settings.cache_enabled:
                await cache_manager.set(cache_key, folder_names, ttl=600)  # 10 minutes
                logger.info(f"Cached {len(folder_names)} folder names")
            
            logger.info(f"Successfully retrieved {len(folder_names)} unique folders")
            return folder_names
            
    except Exception as e:
        logger.error(f"Error retrieving folders: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# New endpoint: Get image count by folder
@app.get("/folders/{folder_name}/count")
async def get_image_count_by_folder(folder_name: str):
    """
    Obtiene el conteo de imágenes para un folder específico
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    try:
        async with pool.acquire() as connection:
            query = "SELECT COUNT(*) as count FROM images_fcl_drive WHERE folder_name = $1"
            result = await connection.fetchrow(query, folder_name)
            
            return {
                "folder_name": folder_name,
                "image_count": result['count']
            }
            
    except Exception as e:
        logger.error(f"Error counting images for folder {folder_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# New endpoint: Batch processing for multiple folders
@app.post("/images/batch-folders")
async def get_images_batch_folders(folder_names: List[str]):
    """
    Obtiene imágenes para múltiples folders de forma simultánea
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    if not folder_names:
        raise HTTPException(status_code=400, detail="Lista de folder_names no puede estar vacía")
    
    if len(folder_names) > 10:  # Limit batch size
        raise HTTPException(status_code=400, detail="Máximo 10 folders por batch")
    
    try:
        # Execute all queries concurrently
        async def get_folder_images(folder_name: str):
            async with pool.acquire() as connection:
                query = """
                SELECT folder_name, COUNT(*) as count
                FROM images_fcl_drive
                WHERE folder_name = $1
                GROUP BY folder_name
                """
                result = await connection.fetchrow(query, folder_name)
                return {
                    "folder_name": folder_name,
                    "image_count": result['count'] if result else 0
                }
        
        # Run all queries concurrently
        tasks = [get_folder_images(folder_name) for folder_name in folder_names]
        results = await asyncio.gather(*tasks)
        
        return {
            "total_folders": len(folder_names),
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Cache management endpoints
@app.get("/cache/stats")
async def get_cache_stats():
    """
    Obtiene estadísticas detalladas del cache
    """
    return await cache_manager.get_stats()

@app.delete("/cache/clear")
async def clear_cache():
    """
    Limpia todo el cache
    """
    try:
        deleted_count = await cache_manager.clear_pattern("*")
        return {
            "message": "Cache cleared successfully",
            "deleted_entries": deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

@app.delete("/cache/clear/{folder_name}")
async def clear_folder_cache(folder_name: str):
    """
    Limpia el cache para un folder específico
    """
    try:
        cache_key = cache_manager._generate_cache_key(
            "images_by_folder",
            folder_name=folder_name
        )
        success = await cache_manager.delete(cache_key)
        
        return {
            "message": f"Cache cleared for folder: {folder_name}",
            "success": success
        }
    except Exception as e:
        logger.error(f"Error clearing folder cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing folder cache: {str(e)}")

@app.post("/cache/warm-up")
async def warm_up_cache():
    """
    Pre-carga el cache con los folders más comunes
    """
    try:
        # Obtener lista de folders (esto se cacheará)
        folders = await get_all_folders(use_cache=True)
        
        # Pre-cargar los primeros 10 folders más comunes
        warm_up_folders = folders[:10] if len(folders) >= 10 else folders
        
        warmed_count = 0
        for folder_name in warm_up_folders:
            try:
                # Simular request para cachear
                request = FolderRequest(folder_name=folder_name)
                await get_images_by_folder(request, use_cache=True)
                warmed_count += 1
            except HTTPException as e:
                if e.status_code == 404:
                    # Es normal que algunos folders no tengan imágenes
                    continue
                else:
                    raise
        
        return {
            "message": "Cache warm-up completed",
            "warmed_folders": warmed_count,
            "total_folders": len(warm_up_folders)
        }
        
    except Exception as e:
        logger.error(f"Error warming up cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error warming up cache: {str(e)}")

# ============================================================================
# PRESENTACIONES ENDPOINTS
# ============================================================================

@app.get("/presentaciones", response_model=List[PresentacionResponse])
async def get_all_presentaciones(
    use_cache: bool = Query(True, description="Usar cache para la respuesta"),
    limit: Optional[int] = Query(None, description="Límite de resultados", ge=1, le=1000),
    offset: Optional[int] = Query(0, description="Offset para paginación", ge=0)
):
    """
    Obtiene todas las presentaciones con paginación opcional y cache
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    # Generate cache key
    cache_key = cache_manager._generate_cache_key(
        "presentaciones_all",
        limit=limit,
        offset=offset
    )
    
    try:
        # Try to get from cache if enabled
        if use_cache and settings.cache_enabled:
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for presentaciones list (limit: {limit}, offset: {offset})")
                return [PresentacionResponse(**item) for item in cached_result]
        
        async with pool.acquire() as connection:
            # Build query with optional pagination
            base_query = """
            SELECT 
                id,
                descripcion_producto,
                peso_caja,
                sobre_peso,
                esquinero_adicionales,
                created_at,
                updated_at
            FROM presentaciones
            ORDER BY created_at DESC
            """
            
            if limit is not None:
                query = base_query + f" LIMIT {limit} OFFSET {offset}"
            else:
                query = base_query
            
            rows = await connection.fetch(query)
            
            presentaciones = [
                PresentacionResponse(
                    id=row['id'],
                    descripcion_producto=row['descripcion_producto'],
                    peso_caja=float(row['peso_caja']),
                    sobre_peso=float(row['sobre_peso']),
                    esquinero_adicionales=row['esquinero_adicionales'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]
            
            # Save to cache if enabled
            if use_cache and settings.cache_enabled:
                cache_data = [presentacion.model_dump() for presentacion in presentaciones]
                await cache_manager.set(cache_key, cache_data)
                logger.info(f"Cached {len(presentaciones)} presentaciones")
            
            logger.info(f"Successfully retrieved {len(presentaciones)} presentaciones")
            return presentaciones
            
    except Exception as e:
        logger.error(f"Error retrieving presentaciones: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/presentaciones/{presentacion_id}", response_model=PresentacionResponse)
async def get_presentacion_by_id(
    presentacion_id: int,
    use_cache: bool = Query(True, description="Usar cache para la respuesta")
):
    """
    Obtiene una presentación específica por ID
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    # Generate cache key
    cache_key = cache_manager._generate_cache_key(
        "presentacion_by_id",
        presentacion_id=presentacion_id
    )
    
    try:
        # Try to get from cache if enabled
        if use_cache and settings.cache_enabled:
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for presentacion ID: {presentacion_id}")
                return PresentacionResponse(**cached_result)
        
        async with pool.acquire() as connection:
            query = """
            SELECT 
                id,
                descripcion_producto,
                peso_caja,
                sobre_peso,
                esquinero_adicionales,
                created_at,
                updated_at
            FROM presentaciones
            WHERE id = $1
            """
            
            row = await connection.fetchrow(query, presentacion_id)
            
            if not row:
                raise HTTPException(
                    status_code=404,
                    detail=f"Presentación con ID {presentacion_id} no encontrada"
                )
            
            presentacion = PresentacionResponse(
                id=row['id'],
                descripcion_producto=row['descripcion_producto'],
                peso_caja=float(row['peso_caja']),
                sobre_peso=float(row['sobre_peso']),
                esquinero_adicionales=row['esquinero_adicionales'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
            # Save to cache if enabled
            if use_cache and settings.cache_enabled:
                await cache_manager.set(cache_key, presentacion.model_dump())
                logger.info(f"Cached presentacion ID: {presentacion_id}")
            
            logger.info(f"Successfully retrieved presentacion ID: {presentacion_id}")
            return presentacion
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving presentacion {presentacion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.post("/presentaciones", response_model=PresentacionResponse, status_code=201)
async def create_presentacion(presentacion: PresentacionCreate):
    """
    Crea una nueva presentación
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    try:
        async with pool.acquire() as connection:
            query = """
            INSERT INTO presentaciones (
                descripcion_producto,
                peso_caja,
                sobre_peso,
                esquinero_adicionales,
                created_at,
                updated_at
            ) VALUES ($1, $2, $3, $4, NOW(), NOW())
            RETURNING 
                id,
                descripcion_producto,
                peso_caja,
                sobre_peso,
                esquinero_adicionales,
                created_at,
                updated_at
            """
            
            row = await connection.fetchrow(
                query,
                presentacion.descripcion_producto,
                presentacion.peso_caja,
                presentacion.sobre_peso,
                presentacion.esquinero_adicionales
            )
            
            new_presentacion = PresentacionResponse(
                id=row['id'],
                descripcion_producto=row['descripcion_producto'],
                peso_caja=float(row['peso_caja']),
                sobre_peso=float(row['sobre_peso']),
                esquinero_adicionales=row['esquinero_adicionales'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
            # Clear related cache entries
            if settings.cache_enabled:
                await cache_manager.clear_pattern("presentaciones_all*")
                logger.info("Cleared presentaciones list cache after creation")
            
            logger.info(f"Successfully created presentacion ID: {new_presentacion.id}")
            return new_presentacion
            
    except Exception as e:
        logger.error(f"Error creating presentacion: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.put("/presentaciones/{presentacion_id}", response_model=PresentacionResponse)
async def update_presentacion(presentacion_id: int, presentacion: PresentacionUpdate):
    """
    Actualiza una presentación existente
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    try:
        async with pool.acquire() as connection:
            # First check if the presentacion exists
            check_query = "SELECT id FROM presentaciones WHERE id = $1"
            exists = await connection.fetchval(check_query, presentacion_id)
            
            if not exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"Presentación con ID {presentacion_id} no encontrada"
                )
            
            # Build dynamic update query based on provided fields
            update_fields = []
            values = []
            param_count = 1
            
            if presentacion.descripcion_producto is not None:
                update_fields.append(f"descripcion_producto = ${param_count}")
                values.append(presentacion.descripcion_producto)
                param_count += 1
            
            if presentacion.peso_caja is not None:
                update_fields.append(f"peso_caja = ${param_count}")
                values.append(presentacion.peso_caja)
                param_count += 1
            
            if presentacion.sobre_peso is not None:
                update_fields.append(f"sobre_peso = ${param_count}")
                values.append(presentacion.sobre_peso)
                param_count += 1
            
            if presentacion.esquinero_adicionales is not None:
                update_fields.append(f"esquinero_adicionales = ${param_count}")
                values.append(presentacion.esquinero_adicionales)
                param_count += 1
            
            if not update_fields:
                raise HTTPException(
                    status_code=400,
                    detail="No se proporcionaron campos para actualizar"
                )
            
            # Add updated_at field
            update_fields.append(f"updated_at = ${param_count}")
            values.append("NOW()")
            param_count += 1
            
            # Add presentacion_id for WHERE clause
            values.append(presentacion_id)
            
            query = f"""
            UPDATE presentaciones 
            SET {', '.join(update_fields)}
            WHERE id = ${param_count}
            RETURNING 
                id,
                descripcion_producto,
                peso_caja,
                sobre_peso,
                esquinero_adicionales,
                created_at,
                updated_at
            """
            
            # Replace NOW() with actual function call for updated_at
            if "updated_at = $" in query:
                query = query.replace(f"updated_at = ${param_count-1}", "updated_at = NOW()")
                values.pop(-2)  # Remove the NOW() string from values
            
            row = await connection.fetchrow(query, *values)
            
            updated_presentacion = PresentacionResponse(
                id=row['id'],
                descripcion_producto=row['descripcion_producto'],
                peso_caja=float(row['peso_caja']),
                sobre_peso=float(row['sobre_peso']),
                esquinero_adicionales=row['esquinero_adicionales'],
                created_at=row['created_at'],
                updated_at=row['updated_at']
            )
            
            # Clear related cache entries
            if settings.cache_enabled:
                await cache_manager.clear_pattern("presentaciones_all*")
                cache_key = cache_manager._generate_cache_key(
                    "presentacion_by_id",
                    presentacion_id=presentacion_id
                )
                await cache_manager.delete(cache_key)
                logger.info(f"Cleared cache for presentacion ID: {presentacion_id}")
            
            logger.info(f"Successfully updated presentacion ID: {presentacion_id}")
            return updated_presentacion
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating presentacion {presentacion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.delete("/presentaciones/{presentacion_id}")
async def delete_presentacion(presentacion_id: int):
    """
    Elimina una presentación
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    try:
        async with pool.acquire() as connection:
            # First check if the presentacion exists
            check_query = "SELECT id FROM presentaciones WHERE id = $1"
            exists = await connection.fetchval(check_query, presentacion_id)
            
            if not exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"Presentación con ID {presentacion_id} no encontrada"
                )
            
            # Delete the presentacion
            delete_query = "DELETE FROM presentaciones WHERE id = $1"
            await connection.execute(delete_query, presentacion_id)
            
            # Clear related cache entries
            if settings.cache_enabled:
                await cache_manager.clear_pattern("presentaciones_all*")
                cache_key = cache_manager._generate_cache_key(
                    "presentacion_by_id",
                    presentacion_id=presentacion_id
                )
                await cache_manager.delete(cache_key)
                logger.info(f"Cleared cache for deleted presentacion ID: {presentacion_id}")
            
            logger.info(f"Successfully deleted presentacion ID: {presentacion_id}")
            return {"message": f"Presentación con ID {presentacion_id} eliminada exitosamente"}
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting presentacion {presentacion_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Cache management for presentaciones
@app.delete("/cache/presentaciones/clear")
async def clear_presentaciones_cache():
    """
    Limpia todo el cache relacionado con presentaciones
    """
    try:
        deleted_count = await cache_manager.clear_pattern("presentaciones*")
        deleted_count += await cache_manager.clear_pattern("presentacion_by_id*")
        
        return {
            "message": "Cache de presentaciones limpiado exitosamente",
            "deleted_entries": deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing presentaciones cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

# ============================================================================
# PHL_PT_ALL_TABLA ENDPOINTS
# ============================================================================

@app.get("/phl-pt-all-tabla", response_model=List[PhlPtAllTablaResponse])
async def get_all_phl_pt_all_tabla(
    use_cache: bool = Query(True, description="Usar cache para la respuesta"),
    limit: Optional[int] = Query(None, description="Límite de resultados", ge=1, le=10000),
    offset: Optional[int] = Query(0, description="Offset para paginación", ge=0)
):
    """
    Obtiene todos los registros de phl_pt_all_tabla con paginación opcional y cache
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    # Generate cache key
    cache_key = cache_manager._generate_cache_key(
        "phl_pt_all_tabla_all",
        limit=limit,
        offset=offset
    )
    
    try:
        # Try to get from cache if enabled
        if use_cache and settings.cache_enabled:
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for phl_pt_all_tabla list (limit: {limit}, offset: {offset})")
                return [PhlPtAllTablaResponse(**item) for item in cached_result]
        
        async with pool.acquire() as connection:
            # Build query with optional pagination
            base_query = """
            SELECT 
                id,
                envio,
                semana,
                fecha_produccion,
                fecha_cosecha,
                cliente,
                tipo_pallet,
                contenedor,
                descripcion_producto,
                destino,
                fundo,
                variedad,
                n_cajas,
                n_pallet,
                turno,
                linea,
                phl_origen,
                materiales_adicionales,
                observaciones,
                sobre_peso,
                peso_caja,
                exportable,
                estado,
                created_at,
                updated_at
            FROM phl_pt_all_tabla
            ORDER BY fecha_produccion DESC, id DESC
            """
            
            if limit is not None:
                query = base_query + f" LIMIT {limit} OFFSET {offset}"
            else:
                query = base_query
            
            rows = await connection.fetch(query)
            
            records = [
                PhlPtAllTablaResponse(
                    id=row['id'],
                    envio=row['envio'],
                    semana=float(row['semana']) if row['semana'] is not None else None,
                    fecha_produccion=row['fecha_produccion'],
                    fecha_cosecha=row['fecha_cosecha'],
                    cliente=row['cliente'],
                    tipo_pallet=row['tipo_pallet'],
                    contenedor=row['contenedor'],
                    descripcion_producto=row['descripcion_producto'],
                    destino=row['destino'],
                    fundo=row['fundo'],
                    variedad=row['variedad'],
                    n_cajas=float(row['n_cajas']) if row['n_cajas'] is not None else None,
                    n_pallet=row['n_pallet'],
                    turno=float(row['turno']) if row['turno'] is not None else None,
                    linea=float(row['linea']) if row['linea'] is not None else None,
                    phl_origen=row['phl_origen'],
                    materiales_adicionales=row['materiales_adicionales'],
                    observaciones=row['observaciones'],
                    sobre_peso=row['sobre_peso'],
                    peso_caja=float(row['peso_caja']) if row['peso_caja'] is not None else None,
                    exportable=float(row['exportable']) if row['exportable'] is not None else None,
                    estado=row['estado'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]
            
            # Save to cache if enabled
            if use_cache and settings.cache_enabled:
                cache_data = [record.model_dump() for record in records]
                await cache_manager.set(cache_key, cache_data)
                logger.info(f"Cached {len(records)} phl_pt_all_tabla records")
            
            logger.info(f"Successfully retrieved {len(records)} phl_pt_all_tabla records")
            return records
            
    except Exception as e:
        logger.error(f"Error retrieving phl_pt_all_tabla records: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@app.get("/phl-pt-all-tabla/by-date-range", response_model=List[PhlPtAllTablaResponse])
async def get_phl_pt_all_tabla_by_date_range(
    fecha_inicio: str = Query(..., description="Fecha de inicio (YYYY-MM-DD)"),
    fecha_fin: str = Query(..., description="Fecha de fin (YYYY-MM-DD)"),
    use_cache: bool = Query(True, description="Usar cache para la respuesta"),
    limit: Optional[int] = Query(None, description="Límite de resultados", ge=1, le=10000),
    offset: Optional[int] = Query(0, description="Offset para paginación", ge=0)
):
    """
    Obtiene registros de phl_pt_all_tabla filtrados por rango de fecha_produccion
    """
    if not pool:
        raise HTTPException(status_code=500, detail="Database pool not available")
    
    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(fecha_inicio, "%Y-%m-%d")
        datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )
    
    # Generate cache key
    cache_key = cache_manager._generate_cache_key(
        "phl_pt_all_tabla_date_range",
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        limit=limit,
        offset=offset
    )
    
    try:
        # Try to get from cache if enabled
        if use_cache and settings.cache_enabled:
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for phl_pt_all_tabla date range ({fecha_inicio} to {fecha_fin})")
                return [PhlPtAllTablaResponse(**item) for item in cached_result]
        
        async with pool.acquire() as connection:
            # Build query with date range filter
            base_query = """
            SELECT 
                id,
                envio,
                semana,
                fecha_produccion,
                fecha_cosecha,
                cliente,
                tipo_pallet,
                contenedor,
                descripcion_producto,
                destino,
                fundo,
                variedad,
                n_cajas,
                n_pallet,
                turno,
                linea,
                phl_origen,
                materiales_adicionales,
                observaciones,
                sobre_peso,
                peso_caja,
                exportable,
                estado,
                created_at,
                updated_at
            FROM phl_pt_all_tabla
            WHERE fecha_produccion >= $1::date 
            AND fecha_produccion <= $2::date
            ORDER BY fecha_produccion DESC, id DESC
            """
            
            if limit is not None:
                query = base_query + f" LIMIT {limit} OFFSET {offset}"
            else:
                query = base_query
            
            rows = await connection.fetch(query, fecha_inicio, fecha_fin)
            
            records = [
                PhlPtAllTablaResponse(
                    id=row['id'],
                    envio=row['envio'],
                    semana=float(row['semana']) if row['semana'] is not None else None,
                    fecha_produccion=row['fecha_produccion'],
                    fecha_cosecha=row['fecha_cosecha'],
                    cliente=row['cliente'],
                    tipo_pallet=row['tipo_pallet'],
                    contenedor=row['contenedor'],
                    descripcion_producto=row['descripcion_producto'],
                    destino=row['destino'],
                    fundo=row['fundo'],
                    variedad=row['variedad'],
                    n_cajas=float(row['n_cajas']) if row['n_cajas'] is not None else None,
                    n_pallet=row['n_pallet'],
                    turno=float(row['turno']) if row['turno'] is not None else None,
                    linea=float(row['linea']) if row['linea'] is not None else None,
                    phl_origen=row['phl_origen'],
                    materiales_adicionales=row['materiales_adicionales'],
                    observaciones=row['observaciones'],
                    sobre_peso=row['sobre_peso'],
                    peso_caja=float(row['peso_caja']) if row['peso_caja'] is not None else None,
                    exportable=float(row['exportable']) if row['exportable'] is not None else None,
                    estado=row['estado'],
                    created_at=row['created_at'],
                    updated_at=row['updated_at']
                )
                for row in rows
            ]
            
            # Save to cache if enabled
            if use_cache and settings.cache_enabled:
                cache_data = [record.model_dump() for record in records]
                await cache_manager.set(cache_key, cache_data)
                logger.info(f"Cached {len(records)} phl_pt_all_tabla records for date range")
            
            logger.info(f"Successfully retrieved {len(records)} phl_pt_all_tabla records for date range {fecha_inicio} to {fecha_fin}")
            return records
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving phl_pt_all_tabla records by date range: {e}")
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

# Cache management for phl_pt_all_tabla
@app.delete("/cache/phl-pt-all-tabla/clear")
async def clear_phl_pt_all_tabla_cache():
    """
    Limpia todo el cache relacionado con phl_pt_all_tabla
    """
    try:
        deleted_count = await cache_manager.clear_pattern("phl_pt_all_tabla*")
        
        return {
            "message": "Cache de phl_pt_all_tabla limpiado exitosamente",
            "deleted_entries": deleted_count
        }
    except Exception as e:
        logger.error(f"Error clearing phl_pt_all_tabla cache: {e}")
        raise HTTPException(status_code=500, detail=f"Error clearing cache: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Determine the best event loop for the platform
    if sys.platform == "win32":
        # Windows: use asyncio only
        logger.info("Windows detected, using asyncio event loop")
        uvicorn.run(
            app, 
            host=settings.host, 
            port=settings.port,
            workers=1,
            access_log=True,
            log_level="info"
        )
    else:
        # Unix/Linux: try uvloop, fallback to asyncio
        try:
            import uvloop
            logger.info("Using uvloop for optimal performance")
            uvicorn.run(
                app, 
                host=settings.host, 
                port=settings.port,
                workers=1,
                loop="uvloop",
                access_log=True,
                log_level="info"
            )
        except ImportError:
            logger.info("uvloop not available, using asyncio")
            uvicorn.run(
                app, 
                host=settings.host, 
                port=settings.port,
                workers=1,
                access_log=True,
                log_level="info"
            )