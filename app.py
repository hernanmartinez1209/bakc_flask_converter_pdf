from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from flask_cors import CORS
from PIL import Image
import os
import subprocess

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'output'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

soffice_path = os.environ.get('soffice_path', '/usr/bin/libreoffice')

ALLOWED_EXTENSIONS = {'.docx', '.xlsx', '.xls', '.png', '.jpg', '.jpeg'}


def convert_with_libreoffice(input_path, output_folder):
    try:
        subprocess.run([
            soffice_path,
            '--headless',
            '--convert-to', 'pdf',
            '--outdir', output_folder,
            input_path
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'LibreOffice failed: {e}')

def convert_image_to_pdf(input_path, output_path):
    image = Image.open(input_path)
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    image.save(output_path, "PDF")

@app.route('/convert', methods=['POST'])
def convert_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({'error': f'Unsupported file type: {ext}'}), 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(input_path)

    try:
        if ext in ['.docx', '.xlsx', '.xls']:
            convert_with_libreoffice(input_path, OUTPUT_FOLDER)
            output_filename = os.path.splitext(filename)[0] + '.pdf'
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        elif ext in ['.jpg', '.jpeg', '.png']:
            output_filename = os.path.splitext(filename)[0] + '.pdf'
            output_path = os.path.join(OUTPUT_FOLDER, output_filename)
            convert_image_to_pdf(input_path, output_path)
        else:
            return jsonify({'error': 'Unsupported file format'}), 400
    except Exception as e:
        print(f'[ERROR] {e}')
        return jsonify({'error': str(e)}), 500

    if not os.path.exists(output_path):
        return jsonify({'error': 'Conversion failed'}), 500

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
