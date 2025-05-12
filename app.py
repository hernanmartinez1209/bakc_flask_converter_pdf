from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
from docx2pdf import convert as docx_convert
import pandas as pd
from PIL import Image

app = Flask(__name__)
CORS(app, origins=["*"])  # En producción, podrías restringir esto si lo deseas

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

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
            docx_convert(input_path, output_path)

        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(input_path)
            temp_html = os.path.join(UPLOAD_FOLDER, f"{name}.html")
            df.to_html(temp_html, index=False)
            from xhtml2pdf import pisa
            with open(temp_html, 'r', encoding='utf-8') as f_in, open(output_path, 'wb') as f_out:
                pisa.CreatePDF(f_in.read(), dest=f_out)
            os.remove(temp_html)

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
        if os.path.exists(input_path):
            os.remove(input_path)
        # El archivo PDF generado no se elimina para permitir la descarga

@app.route('/')
def index():
    return "API de conversión a PDF: Word, Excel, Imágenes"

if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5180))
    app.run(host="0.0.0.0", port=port)
