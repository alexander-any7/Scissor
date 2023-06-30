from http import HTTPStatus
from urllib.parse import urlparse

import validators
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, abort, fields

from api.models import Url, User
from api.utils import db, update_qr_codes

supported_protocols = ["http", "https"]

user_namespace = Namespace("User", description="users namespace")


user_update_input = user_namespace.model(
    "Update User",
    {
        "firstname": fields.String(required=True, description="An firstname for a user"),
        "lastname": fields.String(required=True, description="An lastname for a user"),
        "custom_domain": fields.String(required=False, description="A preferred custom domain"),
        "remove_custom_domain": fields.Boolean(
            required=False, description="A true or false value to remove the custom domain"
        ),
    },
)

user_update_output = user_namespace.model(
    "User Schema",
    {
        "username": fields.String(),
        "email": fields.String(),
        "firstname": fields.String(),
        "lastname": fields.String(),
        "custom_domain": fields.String(),
    },
)


@user_namespace.route("/profile")
class Profile(Resource):
    @jwt_required()
    @user_namespace.expect(user_update_input)
    @user_namespace.marshal_with(user_update_output)
    def get(self):
        session = db.session
        user_id = get_jwt_identity()
        user = session.get(User, user_id)
        if user is None:
            abort(404, description="User Not Found")
        return user, HTTPStatus.OK


@user_namespace.route("/update-profile")
class UpdateProfile(Resource):  # noqa
    @jwt_required()
    @user_namespace.expect(user_update_input)
    @user_namespace.marshal_with(user_update_output)
    def put(self):
        session = db.session
        user_id = get_jwt_identity()
        user = session.get(User, user_id)
        if user is None:
            abort(404, description="User Not Found")
        data: dict = request.get_json()
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        user_domain = data.get("custom_domain")
        remove_custom_domain = data.get("remove_custom_domain")

        user.firstname = firstname if firstname else user.firstname
        user.lastname = lastname if lastname else user.lastname
        user.custom_domain = "" if remove_custom_domain else user.custom_domain

        if user_domain and not remove_custom_domain:
            parsed_domain = urlparse(user_domain)
            custom_domain = parsed_domain.netloc
            protocol = parsed_domain.scheme

            if not validators.domain(custom_domain):
                abort(HTTPStatus.BAD_REQUEST, f"{user_domain} not a valid domain")

            if protocol and protocol not in supported_protocols:
                abort(HTTPStatus.BAD_REQUEST, f"{protocol} is not a supported protocol")

            if custom_domain[-1] != "/":
                custom_domain = f"{protocol}://{custom_domain}/"
                update_qr_codes(user_id, custom_domain, Url)

            user.custom_domain = custom_domain

        if remove_custom_domain:
            update_qr_codes(user_id, request.host_url, Url)

        user.update()

        return user, HTTPStatus.OK
