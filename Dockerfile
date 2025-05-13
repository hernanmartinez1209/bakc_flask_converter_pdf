# Imagen base con LibreOffice y Python
FROM debian:bullseye-slim

# Instala LibreOffice y dependencias
RUN apt-get update && \
    apt-get install -y libreoffice python3 python3-pip python3-dev python3-venv build-essential poppler-utils && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Crea y activa entorno virtual
WORKDIR /app
COPY . /app

# Instala dependencias Python
RUN pip install --upgrade pip
RUN pip install flask flask-cors pillow

# Define variable de entorno para LibreOffice
ENV soffice_path=/usr/bin/libreoffice

# Puerto que expone Flask
EXPOSE 5000

# Comando para ejecutar la app
CMD ["python3", "app.py"]
