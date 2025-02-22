from flask import Flask
from config import Config
from src.commons.exception.exception_handler import handle_generic_exception


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.register_error_handler(Exception, handle_generic_exception)

    # Register blueprints
    from src.controllers.hello_controller import hello_bp
    app.register_blueprint(hello_bp, url_prefix='/api/v1')

    return app