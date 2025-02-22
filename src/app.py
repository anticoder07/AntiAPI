from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    from src.controllers.hello_controller import hello_bp
    app.register_blueprint(hello_bp, url_prefix='/api/v1')

    return app