from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pandas as pd
from PIL import Image
from io import BytesIO
from xhtml2pdf import pisa
import subprocess

app = Flask(__name__)
CORS(app, origins=["*"])

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def docx_to_pdf(input_path, output_folder):
    try:
        # Verificar si LibreOffice está instalado y accesible
        libreoffice_check = subprocess.run(['libreoffice', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if libreoffice_check.returncode != 0:
            raise EnvironmentError("LibreOffice no está instalado o no es accesible.")

        # Ejecutar la conversión
        subprocess.run([
            'libreoffice',
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_folder,
            input_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al convertir el archivo Word con LibreOffice: {str(e)}") from e
    except EnvironmentError as e:
        raise RuntimeError(f"Error con LibreOffice: {str(e)}") from e

@app.route('/convert', methods=['POST'])
def convert_file_to_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    name, ext = os.path.splitext(filename)
    ext = ext.lower()
    output_filename = f"{name}.pdf"
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)

    try:
        if ext == '.docx':
            # Verificar si el archivo .docx se guardó correctamente
            if not os.path.exists(input_path):
                return jsonify({"error": "El archivo .docx no se guardó correctamente"}), 500

            # Intentar convertir .docx a .pdf
            docx_to_pdf(input_path, UPLOAD_FOLDER)
            if not os.path.exists(output_path):
                raise FileNotFoundError("La conversión no generó un archivo PDF.")

        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path)
            df = df.fillna('')  # Reemplaza NaN por vacío

            html_content = df.to_html(index=False, border=0)

            full_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    table {{ width: 100%; border-collapse: collapse; }}
                    th, td {{ border: 1px solid #000; padding: 4px; text-align: left; }}
                </style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """

            with open(output_path, 'wb') as f_out:
                pisa.CreatePDF(full_html, dest=f_out)

        elif ext in ['.png', '.jpg', '.jpeg']:
            img = Image.open(input_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img.save(output_path, 'PDF')

        else:
            return jsonify({"error": "Tipo de archivo no soportado"}), 400

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Limpiar archivos temporales
        if os.path.exists(input_path):
            os.remove(input_path)

@app.route('/')
def index():
    return "API de conversión a PDF: Word, Excel, Imágenes"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5180))
    app.run(host="0.0.0.0", port=port)
