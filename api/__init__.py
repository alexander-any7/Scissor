from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_restx import Api

from api.auth import auth_namespace
from api.config import config_dict
from api.models import Url, User
from api.url_routes import redirect_namespace, url_namespace
from api.user_routes import user_namespace
from api.utils import cache, db


def create_app(config=config_dict["dev"]):
    app = Flask(__name__)
    app.config.from_object(config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    authorizations = {
        "Bearer Auth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "add a JWT with ** Bearer &lt;JWT&gt; to authorize",
        }
    }
    api = Api(
        app,
        title="Scissor API",
        description="",
        authorizations=authorizations,
        security="Bearer Auth",
        doc="/api/docs",
    )

    db.init_app(app)
    cache.init_app(app)

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
