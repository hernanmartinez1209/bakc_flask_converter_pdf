FROM python:3.10-slim

# Instala LibreOffice y dependencias
RUN apt-get update && \
    apt-get install -y libreoffice && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

# Instala dependencias Python
RUN pip install --upgrade pip
RUN pip install flask flask-cors pillow gunicorn

# Expone el puerto 5000
EXPOSE 5000

# Usa Gunicorn como servidor de producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
