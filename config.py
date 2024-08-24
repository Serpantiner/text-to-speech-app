import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
    AUDIO_FOLDER = os.path.join(os.getcwd(), 'static', 'audio')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB limit