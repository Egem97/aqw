# Dockerfile para Django
FROM python:3.11-slim

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear usuario no-root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER root

# Crear directorios para static y media (incluye STATIC_ROOT)
RUN mkdir -p /app/static /app/staticfiles /app/media && \
    chown -R appuser:appuser /app/static /app/staticfiles /app/media

# Exponer puerto
EXPOSE 8880

# Script de inicio que ejecuta collectstatic y luego gunicorn
COPY docker-entrypoint.sh /app/
RUN chmod +x /app/docker-entrypoint.sh && \
    chown appuser:appuser /app/docker-entrypoint.sh

# Comando de inicio
CMD ["/app/docker-entrypoint.sh"]
