from flask import Flask
from config import Config
from src.commons.exception.exception_handler import handle_generic_exception
import os

def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'src/templates'))
    app.config.from_object(Config)

    app.register_error_handler(Exception, handle_generic_exception)

    from src.controllers.web.authentication_controller import base_web_url
    app.register_blueprint(base_web_url, url_prefix='/web')

    from src.controllers.api.authentication_api_controller import base_api_url
    app.register_blueprint(base_api_url, url_prefix='/api/v1')

    return app
