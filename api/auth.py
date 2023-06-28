from http import HTTPStatus

import validators
from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, abort, fields
from werkzeug.security import check_password_hash, generate_password_hash

from api.models import User
from api.utils import MailService, TokenService, db

auth_namespace = Namespace("Auth", description="auth namespace")

user_register_input = auth_namespace.model(
    "RegisterUser",
    {
        "username": fields.String(required=True, description="An username for a user"),
        "email": fields.String(required=True, description="An email for a user"),
        "firstname": fields.String(required=True, description="An firstname for a user"),
        "lastname": fields.String(required=True, description="An lastname for a user"),
        "password": fields.String(required=True, description="A password for a user"),
        "confirm_password": fields.String(required=True, description="confirm the password"),
    },
)

user_register_output = auth_namespace.model(
    "User",
    {
        "id": fields.Integer(),
        "username": fields.String(),
        "email": fields.String(),
        "firstname": fields.String(),
        "lastname": fields.String(),
        "date_joined": fields.DateTime(),
    },
)

user_login_output = auth_namespace.model(
    "User",
    {
        "access_token": fields.String(),
        "refresh_token": fields.String(),
        "token_type": fields.String(),
    },
)


user_login_input = auth_namespace.model(
    "User",
    {
        "username_or_email": fields.String(required=True, description="username or email"),
        "password": fields.String(required=True, description="password"),
    },
)

password_reset_input = auth_namespace.model(
    "User", {"username_or_email": fields.String(required=True, description="username or email")}
)


logged_in_user_password_reset_input = auth_namespace.model(
    "User",
    {
        "current_password": fields.String(required=True, description="current password"),
        "new_password_1": fields.String(required=True, description="new password"),
        "new_password_2": fields.String(required=True, description="confirm new password"),
    },
)

user_password_reset_confirm = auth_namespace.model(
    "User",
    {
        "password_1": fields.String(required=True, description="new password"),
        "password_2": fields.String(required=True, description="confirm new password"),
    },
)


@auth_namespace.route("/register")
class Users(Resource):
    @auth_namespace.expect(user_register_input)
    @auth_namespace.marshal_with(user_register_output)
    def post(self):
        data: dict = request.get_json()
        username = data.get("username")
        email = data.get("email")
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if not username:
            abort(HTTPStatus.BAD_REQUEST, "Username is required")

        if not validators.email(email):
            abort(HTTPStatus.BAD_REQUEST, "Email is not valid")

        if not password or not confirm_password:
            abort(HTTPStatus.BAD_REQUEST, "Password and Confirm Password cannot be empty")

        if password != confirm_password:
            abort(HTTPStatus.BAD_REQUEST, "Passwords do not match")

        if len(password) < 6:
            abort(HTTPStatus.BAD_REQUEST, "Password is too short")

        if User.query.filter_by(username=username).first():
            abort(HTTPStatus.CONFLICT, "Username is already taken")

        if User.query.filter_by(email=email).first():
            abort(HTTPStatus.CONFLICT, "Email is already taken")

        password_hash = generate_password_hash(password)
        new_user = User(
            username=username, firstname=firstname, lastname=lastname, email=email, password_hash=password_hash
        )
        new_user.save()

        return new_user, HTTPStatus.CREATED


@auth_namespace.route("/login")
class Users(Resource):  # noqa
    @auth_namespace.expect(user_login_input)
    @auth_namespace.marshal_with(user_login_output)
    def post(self):
        data: dict = request.get_json()
        username_or_email = data.get("username_or_email")
        password = data.get("password")

        user = (
            User.query.filter_by(email=username_or_email).first()
            or User.query.filter_by(username=username_or_email).first()
        )

        if user and check_password_hash(user.password_hash, password):
            user.access_token = create_access_token(identity=user.id)
            user.refresh_token = create_refresh_token(identity=user.id)
            user.token_type = "bearer"

            return user, HTTPStatus.OK

        abort(HTTPStatus.UNAUTHORIZED, "Wrong credentials")


@auth_namespace.route("/password-reset-request")
class Users(Resource):  # noqa
    @auth_namespace.expect(password_reset_input)
    def post(self):
        data: dict = request.get_json()
        username_or_email = data.get("username_or_email")

        user = (
            User.query.filter_by(email=username_or_email).first()
            or User.query.filter_by(username=username_or_email).first()
        )

        if not user:
            abort(HTTPStatus.NOT_ACCEPTABLE, "A user with that username or email not found!")

        user_id = str(user.id)
        user_email = user.email
        token = TokenService.create_password_reset_token(user_id=user_id)
        if token:
            is_mail_sent = MailService.send_reset_mail(email=user_email, token=token, uuid=user_id)
            if is_mail_sent:
                return {"message": "An email has been sent with instructions to reset your password."}, HTTPStatus.OK


@auth_namespace.route("/password-reset/<string:token>/<string:uuid>/confirm")
class Users(Resource):  # noqa
    @auth_namespace.expect(user_password_reset_confirm)
    def post(self, token: str, uuid: str):
        session = db.session
        data: dict = request.get_json()
        password_1 = data.get("password_1")
        password_2 = data.get("password_2")

        if password_1 and password_2:
            if password_1 == password_2:
                if len(password_2) < 6:
                    abort(HTTPStatus.BAD_REQUEST, "Password is too short")
                if TokenService.validate_password_reset_token(token=token, user_id=uuid):
                    user = session.get(User, uuid)
                    if user:
                        user.password_hash = generate_password_hash(password_2)
                        user.update()
                        return {"message": "Password Reset Successfully"}, HTTPStatus.OK
                else:
                    return {"message": "Unable to verify token"}, HTTPStatus.BAD_REQUEST
        return {"message": "Passwords do not match"}, HTTPStatus.BAD_REQUEST


@auth_namespace.route("/reset-password")
class Users(Resource):  # noqa
    @auth_namespace.expect(logged_in_user_password_reset_input)
    @jwt_required()
    def post(self):
        session = db.session
        user_id = get_jwt_identity()
        user = session.get(User, user_id)
        if user is None:
            abort(404, description="User Not Found")
        data: dict = request.get_json()
        current_password = data.get("current_password")
        new_password_1 = data.get("new_password_1")
        new_password_2 = data.get("new_password_2")

        if current_password and check_password_hash(user.password_hash, current_password):
            if new_password_1 and new_password_2:
                if new_password_1 == new_password_2:
                    user.password_hash = generate_password_hash(new_password_2)
                    user.update()
                    return {"message": "Password Reset Successfully"}, HTTPStatus.OK
                else:
                    abort(HTTPStatus.BAD_REQUEST, "Passwords do not match")
            else:
                abort(HTTPStatus.BAD_REQUEST, "New Password and Confirm New Password cannot be empty")
        else:
            abort(HTTPStatus.UNAUTHORIZED, "Current Password is incorrect")


@auth_namespace.route("/refresh")
class Refresh(Resource):  # noqa
    @jwt_required(refresh=True)
    def post(self):
        current_user = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user)
        return {"access_token": new_access_token}, HTTPStatus.OK
