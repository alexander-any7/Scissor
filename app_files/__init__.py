from flask import Flask
from flask_restx import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager

from app_files.utils import db
from app_files.models import User, Url
from app_files.config import config_dict
from app_files.auth import auth_namespace
from app_files.user_routes import user_namespace
from app_files.url_routes import url_namespace, redirect_namespace

def create_app(config=config_dict['dev']):
    app = Flask(__name__)
    app.config.from_object(config)

    authorizations = {
        "Bearer Auth" : {
            'type' : "apiKey",
            "in" : "header",
            "name" : 'Authorization',
            "description" : "add a JWT with ** Bearer &lt;JWT&gt; to authorize"
        }
    }
    api = Api(app,
          title="Scissor API",
          description="",
          authorizations=authorizations,
          security="Bearer Auth"
    )

    db.init_app(app)

    migrate = Migrate(app, db)
    jwt = JWTManager(app)

    
    api.add_namespace(auth_namespace, path='/auth')
    api.add_namespace(user_namespace, path='/users')
    api.add_namespace(url_namespace, path='/urls')
    api.add_namespace(redirect_namespace, path='/')

    @app.shell_context_processor
    def make_shell_context():
        return{
            'db':db,
            'User' : User,
            'Url' : Url
            }


    return app
