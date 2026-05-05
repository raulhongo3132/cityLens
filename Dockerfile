# Usa la imagen oficial de Python que recomienda la guía
FROM python:3.12-slim

# Evita que Python genere archivos .pyc y permite ver logs en tiempo real
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos dependencias del sistema necesarias para psycopg2 (PostgreSQL)
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*

# Copiamos el archivo de librerías
COPY requirements.txt .

# Instalamos las librerías de tu proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos el resto del código[cite: 1]
COPY . .

# Comando para ejecutar la app (ajustado a tu archivo run.py)[cite: 1]
CMD ["python", "run.py"]