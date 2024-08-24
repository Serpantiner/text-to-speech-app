from flask import Flask
from flask_cors import CORS
from config import Config

def create_app():
    app = Flask(__name__, static_folder='../static', static_url_path='')
    app.config.from_object(Config)
    CORS(app)

    from app import routes
    app.register_blueprint(routes.main)

    @app.route('/')
    def index():
        return app.send_static_file('index.html')

    return app