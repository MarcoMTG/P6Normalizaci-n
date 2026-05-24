# Usamos la versión de PostgreSQL optimizada sobre Alpine Linux
FROM postgres:15-alpine

# Seteamos la zona horaria del contenedor para mantener consistencia en los datos clínicos
ENV TZ=America/Mexico_City

# Exponemos el puerto estándar de PostgreSQL hacia la red interna de Docker
EXPOSE 5432