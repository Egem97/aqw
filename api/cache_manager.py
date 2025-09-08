import json
import hashlib
import asyncio
from typing import Any, Optional, Union
from datetime import datetime, timedelta
import logging
from cachetools import TTLCache
from config import settings

logger = logging.getLogger(__name__)

class CacheManager:
    """
    Sistema de cache en memoria optimizado para máximo rendimiento
    """
    
    def __init__(self):
        self.memory_cache = TTLCache(
            maxsize=settings.memory_cache_size, 
            ttl=settings.cache_ttl_seconds
        )
        self.redis_available = False
        
    async def initialize(self):
        """Inicializar cache en memoria"""
        if not settings.cache_enabled:
            logger.info("Cache disabled in settings")
            return
            
        logger.info(f"Memory cache initialized with {settings.memory_cache_size} max items and {settings.cache_ttl_seconds}s TTL")
    
    async def close(self):
        """Limpiar cache en memoria"""
        self.memory_cache.clear()
        logger.info("Memory cache cleared")
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generar clave de cache única"""
        # Crear string con todos los parámetros
        params_str = json.dumps(kwargs, sort_keys=True, default=str)
        
        # Generar hash para evitar claves muy largas
        hash_obj = hashlib.md5(params_str.encode())
        hash_str = hash_obj.hexdigest()[:16]  # Usar solo los primeros 16 caracteres
        
        return f"{prefix}:{hash_str}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Obtener valor del cache"""
        if not settings.cache_enabled:
            return None
            
        try:
            if key in self.memory_cache:
                logger.debug(f"Cache hit: {key}")
                return self.memory_cache[key]
                
            logger.debug(f"Cache miss: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Guardar valor en cache"""
        if not settings.cache_enabled:
            return False
            
        try:
            # Guardar en memoria
            self.memory_cache[key] = value
            logger.debug(f"Cache set: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Eliminar valor del cache"""
        if not settings.cache_enabled:
            return False
            
        try:
            # Eliminar de memoria
            if key in self.memory_cache:
                del self.memory_cache[key]
                logger.debug(f"Cache deleted: {key}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def clear_pattern(self, pattern: str) -> int:
        """Eliminar todas las claves que coincidan con un patrón"""
        if not settings.cache_enabled:
            return 0
            
        deleted_count = 0
        
        try:
            # Limpiar memoria
            if pattern == "*":
                deleted_count = len(self.memory_cache)
                self.memory_cache.clear()
            else:
                keys_to_delete = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
                for key in keys_to_delete:
                    del self.memory_cache[key]
                    deleted_count += 1
            
            logger.info(f"Cleared {deleted_count} cache entries matching pattern: {pattern}")
            return deleted_count
            
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
    
    async def get_stats(self) -> dict:
        """Obtener estadísticas del cache"""
        stats = {
            "enabled": settings.cache_enabled,
            "redis_available": self.redis_available,
            "memory_cache_size": len(self.memory_cache),
            "memory_cache_maxsize": self.memory_cache.maxsize,
            "ttl_seconds": settings.cache_ttl_seconds,
            "cache_type": "memory_only"
        }
        
        return stats

# Cache decorador para endpoints
def cached(ttl: int = None, key_prefix: str = "api"):
    """
    Decorador para cachear resultados de endpoints
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if not settings.cache_enabled:
                return await func(*args, **kwargs)
            
            # Generar clave de cache
            cache_key = cache_manager._generate_cache_key(
                f"{key_prefix}:{func.__name__}",
                args=args,
                kwargs=kwargs
            )
            
            # Intentar obtener del cache
            cached_result = await cache_manager.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Ejecutar función y cachear resultado
            result = await func(*args, **kwargs)
            await cache_manager.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

# Instancia global del cache manager
cache_manager = CacheManager()
