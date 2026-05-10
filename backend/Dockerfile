# Usamos la versión de Python solicitada (3.13 para estabilidad, extensible a 3.14)
FROM python:3.13-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo
WORKDIR /app

# Instalamos dependencias del sistema necesarias para psycopg2 y Pillow
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libopenjp2-7-dev \
    libtiff5-dev \
    tk-dev \
    tcl-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalamos dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el código del proyecto
COPY . .

# Creamos la carpeta media para las subidas de vídeo
RUN mkdir -p /app/media/videos /app/staticfiles

# Damos permisos de ejecución al entrypoint
RUN chmod +x /app/entrypoint.sh

# Puerto en el que corre Django
EXPOSE 8000

# Usamos el script de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
