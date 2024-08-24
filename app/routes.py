from flask import Blueprint, request, jsonify, current_app
from werkzeug.utils import secure_filename
import os
from app.pdf_processor import read_pdf
from app.text_to_speech import text_to_speech
from app.utils import allowed_file

main = Blueprint('main', __name__)

@main.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    language = request.form.get('language', 'en-US')

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            pdf_text = read_pdf(file_path)
            output_file = os.path.join(current_app.config['AUDIO_FOLDER'], f"{os.path.splitext(filename)[0]}.wav")
            text_to_speech(pdf_text, language, output_file)

            audio_url = f"/static/audio/{os.path.basename(output_file)}"
            return jsonify({'audioUrl': audio_url}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.remove(file_path)  # Clean up the uploaded PDF file
    
    return jsonify({'error': 'File type not allowed'}), 400