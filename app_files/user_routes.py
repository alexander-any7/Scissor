import os
from http import HTTPStatus
from urllib.parse import urlparse

import qrcode
import validators
from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, abort, fields

from app_files.models import Url, User

supported_protocols = ["http", "https"]

user_namespace = Namespace("User", description="users namespace")


user_update_input = user_namespace.model(
    "RegisterUser",
    {
        "firstname": fields.String(required=True, description="An firstname for a user"),
        "lastname": fields.String(required=True, description="An lastname for a user"),
        "custom_domain": fields.String(required=False, description="A preferred custom domain"),
    },
)

user_update_output = user_namespace.model(
    "User",
    {
        "username": fields.String(),
        "email": fields.String(),
        "firstname": fields.String(),
        "lastname": fields.String(),
        "custom_domain": fields.String(),
    },
)


@user_namespace.route("/profile")
class Users(Resource):
    @jwt_required()
    @user_namespace.expect(user_update_input)
    @user_namespace.marshal_with(user_update_output)
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return user, HTTPStatus.OK


@user_namespace.route("/update-profile")
class Users(Resource):  # noqa
    @jwt_required()
    @user_namespace.expect(user_update_input)
    @user_namespace.marshal_with(user_update_output)
    def put(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        data: dict = request.get_json()
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        user_domain = data.get("custom_domain")
        remove_custom_domain = data.get('remove_custom_domain')

        user.firstname = firstname if firstname else user.firstname
        user.lastname = lastname if lastname else user.lastname
        user.custom_domain = "" if remove_custom_domain else user.custom_domain

        if user_domain and not remove_custom_domain:
            parsed_domain = urlparse(user_domain)
            custom_domain = parsed_domain.netloc
            protocol = parsed_domain.scheme

            if not validators.domain(custom_domain):
                abort(HTTPStatus.BAD_REQUEST, f"{custom_domain} is not a valid domain")

            if protocol and protocol not in supported_protocols:
                abort(HTTPStatus.BAD_REQUEST, f"{protocol} is not a supported protocol")

            if custom_domain[-1] != "/":
                custom_domain = custom_domain + "/"
                urls = Url.query.filter_by(user_id=user_id).all()
                for url in urls:
                    if url.qr_code:
                        file_path = url.qr_code
                        if os.path.exists(file_path):
                            img = qrcode.make(f"{protocol}{custom_domain}{url.uuid}?referrer=qr")
                            img.save(file_path)

            user.custom_domain = f"{protocol}://{custom_domain}"

        user.update()

        return user, HTTPStatus.OK
