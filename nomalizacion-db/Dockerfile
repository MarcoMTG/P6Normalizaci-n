# ============================================================
# Dockerfile — Normalización E-commerce (Práctica 6)
# ============================================================
FROM python:3.11-slim

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar dependencias primero (aprovecha caché de Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el proyecto
COPY scripts/ ./scripts/
COPY sql/     ./sql/
COPY docs/    ./docs/

# Crear carpetas de datos (el volumen se monta aquí)
RUN mkdir -p data/raw data/normalized/ecommerce

# Script de entrada
CMD ["python", "scripts/normalize_dataset2.py"]
