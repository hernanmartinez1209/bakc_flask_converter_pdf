# Usamos una imagen base de Python
FROM python:3.9-slim

# Instalar LibreOffice (y otras dependencias necesarias)
RUN apt-get update && \
    apt-get install -y libreoffice libreoffice-common && \
    apt-get clean

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# Copiar los archivos de tu proyecto al contenedor
COPY . /app

# Instalar las dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt

# Exponer el puerto 5000 (el puerto predeterminado de Flask)
EXPOSE 5000

# Comando para ejecutar la API Flask
CMD ["python", "app.py"]
