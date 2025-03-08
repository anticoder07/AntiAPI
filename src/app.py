import os

from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from config import Config
from src.commons.database.mySql.config_connect_my_sql import db
from src.commons.exception.exception_handler import handle_generic_exception


def create_app():
    app = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'src/templates'))
    app.config.from_object(Config)

    app.register_error_handler(Exception, handle_generic_exception)

    from src.controllers.web.authentication_controller import base_web_url
    app.register_blueprint(base_web_url, url_prefix='/web')

    from src.controllers.api.project_controller import base_api_url_project
    app.register_blueprint(base_api_url_project, url_prefix='/api/v1/projects')

    from src.controllers.api.topic_controller import base_api_url_topic
    app.register_blueprint(base_api_url_topic, url_prefix='/api/v1/topics')

    from src.controllers.api.file_controller import base_api_url_file
    app.register_blueprint(base_api_url_file, url_prefix='/api/v1/files')

    from src.controllers.api.api_controller import base_api_url_api
    app.register_blueprint(base_api_url_api, url_prefix='/api/v1/apis')

    from src.controllers.api.auth_controller import base_api_url_auth
    app.register_blueprint(base_api_url_auth, url_prefix='/api/v1/auth')

    from src.controllers.api.vul_controller import base_api_url_vul
    app.register_blueprint(base_api_url_vul, url_prefix='/api/v1/vul')

    from src.controllers.api.company_controller import base_api_url_company
    app.register_blueprint(base_api_url_company, url_prefix='/api/v1/companies')

    from src.controllers.api.payload_controller import base_api_url_payload
    app.register_blueprint(base_api_url_payload, url_prefix='/api/v1/payloads')


    db.init_app(app)
    with app.app_context():
        db.create_all()

    CORS(app, resources={r"/api/*": {"origins": ["http://127.0.0.1:5000", "http://localhost:5000"]}})

    JWTManager(app)

    return app
