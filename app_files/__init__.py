from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api

from app_files.auth import auth_namespace
from app_files.config import config_dict
from app_files.models import Url, User
from app_files.url_routes import redirect_namespace, url_namespace
from app_files.user_routes import user_namespace
from app_files.utils import db


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)
    app.config.from_object(config)

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "add a JWT with ** Bearer &lt;JWT&gt; to authorize",
        }
    }
    api = Api(app, title="Scissor API", description="", authorizations=authorizations, security="Bearer Auth")  # noqa

    db.init_app(app)

    migrate = Migrate(app, db)  # noqa
    jwt = JWTManager(app)  # noqa

    api.add_namespace(auth_namespace, path="/auth")
    api.add_namespace(user_namespace, path="/users")
    api.add_namespace(url_namespace, path="/urls")
    api.add_namespace(redirect_namespace, path="/")

    @app.shell_context_processor
    def make_shell_context():
        return {"db": db, "User": User, "Url": Url}

    return app
    return app
