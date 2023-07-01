import json
import os
from http import HTTPStatus

import qrcode
import shortuuid
import validators
from decouple import config
from flask import redirect, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_restx import Namespace, Resource, abort, fields

from api.config import BASE_DIR
from api.models import DeletedUrl, Url, User
from api.utils import cache, db, limiter, convert_referrer

DEFAULT_DOMAIN = config("DEFAULT_DOMAIN")

# Get the directory where qr code images will be stored
script_dir = os.path.dirname(os.path.abspath(__file__))
qr_codes_dir = f"{os.path.dirname(BASE_DIR)}\\frontend\\public\\qr_codes"


url_namespace = Namespace("Url", description="urls namespace")
redirect_namespace = Namespace("Redirect", description="redirect namespace")

# redis_client = redis.Redis(host='localhost', port=5000, db=0)

url_input = url_namespace.model(
    "Shorten Url",
    {
        "url": fields.String(required=True, description="url to shorten"),
    },
)

url_input_update = url_namespace.model(
    "Update Url",
    {
        "url": fields.String(required=True, description="url to shorten"),
        "title": fields.String(required=False),
        "use_default_domain": fields.Boolean(description="To use default domain", default=False),
    },
)

url_output = url_namespace.model(
    "Url Output",
    {
        "uuid": fields.String(),
        "short_url": fields.String(),
        "long_url": fields.String(),
        "title": fields.String(),
        "created_at": fields.DateTime(),
        "updated_at": fields.DateTime(),
        "clicks": fields.Integer(),
        "referrer": fields.Raw(),
        "qr_code": fields.String(),
        "has_qr_code": fields.Boolean(),
    },
)

deleted_url_output = url_namespace.model(
    "Deleted Url Output",
    {
        "id": fields.Integer(),
        "long_url": fields.String(),
        "created_at": fields.DateTime(),
        "deleted_at": fields.DateTime(),
    },
)


@url_namespace.route("/shorten-url")
class ShortenUrl(Resource):
    """Shorten a URL
    Accepts [POST] requests
    Returns a serialized URL object
    """
    @limiter.limit("100/minute")
    @cache.cached(timeout=60)
    @jwt_required()
    @url_namespace.expect(url_input)
    @url_namespace.marshal_with(url_output)
    def post(self):
        user = get_jwt_identity()
        data: dict = request.get_json()
        url = data.get("url")
        title = data.get("title")
        user_domain = User.query.filter_by(id=user).first().custom_domain

        domain = f"{user_domain}" if user_domain else request.host_url

        if not url or not validators.url(url, public=True):
            abort(HTTPStatus.BAD_REQUEST, "A valid URL is required")

        if not title or len(title) > 20:
            abort(HTTPStatus.BAD_REQUEST, "Title is required and should not be longer than 10 characters")

        existing_urls = Url.query.filter_by(long_url=url).all()

        for s_url in existing_urls:
            if s_url.user_id == user:
                s_url.short_url = f"{domain}{s_url.uuid}"
                return s_url, HTTPStatus.OK

        short_url = shortuuid.random(length=6)

        new_url = Url(user_id=user, uuid=short_url, long_url=url, title=title)
        new_url.referrer = json.dumps({"Unknowns": 0})
        new_url.save()

        new_url.short_url = f"{domain}{short_url}"
        return new_url, HTTPStatus.CREATED


@url_namespace.route("/all-urls")
class AllUrls(Resource):
    """Get all shortened URLs
    Accepts [GET] requests
    Returns multiple serialized URL objects
    """
    @limiter.limit("10/minute")
    @cache.cached(timeout=60)
    @jwt_required()
    @url_namespace.marshal_list_with(url_output)
    def get(self):
        user = get_jwt_identity()
        user_domain = User.query.filter_by(id=user).first().custom_domain
        domain = f"{user_domain}" if user_domain else request.host_url
        urls = Url.query.filter_by(user_id=user).all()
        for url in urls:
            convert_referrer(url)
            url.short_url = f"{domain}{url.uuid}"
        return urls, HTTPStatus.OK


@url_namespace.route("/deleted-urls")
class DeletedUrls(Resource):
    """Get all deleted URLs
    Accepts [GET] requests
    Returns multiple serialized Deleted URL objects
    """
    @limiter.limit("10/minute")
    @cache.cached(timeout=60)
    @jwt_required()
    @url_namespace.marshal_list_with(deleted_url_output)
    def get(self):
        user = get_jwt_identity()
        urls = DeletedUrl.query.filter_by(user_id=user).all()
        return urls, HTTPStatus.OK


@url_namespace.route("/restore-url/<int:id>")
class RestoreDeletedUrl(Resource):
    """Restore a deleted URL
    Accepts [GET] requests
    Returns a serialized URL object
    """
    @limiter.limit("10/minute")
    @cache.cached(timeout=60)
    @jwt_required()
    @url_namespace.marshal_with(url_output)
    def get(self, id):
        user = get_jwt_identity()
        url_to_restore = DeletedUrl.query.filter_by(id=id).first()

        if not url_to_restore or url_to_restore.user_id != user:
            abort(HTTPStatus.NOT_FOUND, "Not Found")

        user_domain = User.query.filter_by(id=user).first().custom_domain
        domain = f"{user_domain}" if user_domain else request.host_url

        if not url_to_restore or not validators.url(url_to_restore.long_url, public=True):
            abort(HTTPStatus.BAD_REQUEST, "A valid URL is required")

        url_to_restore.delete()

        existing_urls = Url.query.filter_by(long_url=url_to_restore.long_url).all()

        for s_url in existing_urls:
            if s_url.user_id == user:
                s_url.short_url = f"{domain}{s_url.uuid}"
                return s_url, HTTPStatus.OK

        short_url = shortuuid.random(length=6)

        new_url = Url(user_id=user, uuid=short_url, long_url=url_to_restore.long_url)
        new_url.referrer = json.dumps({"Unknowns": 0})
        new_url.save()

        new_url.short_url = f"{domain}{short_url}"
        return new_url, HTTPStatus.CREATED


@url_namespace.route("/<string:uuid>")
class Urls(Resource):
    """RUD a URL
    Accepts [GET, PUT, DELETE] requests
    Returns a serialized URL object
    """
    @limiter.limit("10/minute")
    @cache.cached(timeout=60)
    @jwt_required()
    @url_namespace.marshal_list_with(url_output)
    def get(self, uuid):
        user = get_jwt_identity()
        user_domain = User.query.filter_by(id=user).first().custom_domain
        domain = f"{user_domain}" if user_domain else request.host_url
        url = Url.query.filter_by(uuid=uuid).first_or_404(description="URL Not Found")

        if url.user_id != user:
            abort(HTTPStatus.NOT_FOUND, "URL Not Found")
        convert_referrer(url)
        url.short_url = f"{domain}{url.uuid}"
        return url, HTTPStatus.OK

    @limiter.limit("10/minute")
    @cache.cached(timeout=10)
    @jwt_required()
    @url_namespace.marshal_list_with(url_output)
    @url_namespace.expect(url_input_update)
    def put(self, uuid):
        user = get_jwt_identity()
        user_domain = User.query.filter_by(id=user).first().custom_domain
        domain = f"{user_domain}" if user_domain else request.host_url
        url_to_update = Url.query.filter_by(uuid=uuid).first_or_404(description="URL Not Found")

        if url_to_update.user_id != user:
            abort(HTTPStatus.NOT_FOUND, "URL Not Found")

        data: dict = request.get_json()
        new_url = data.get("url")
        new_title = data.get("title")

        if new_url and not validators.url(new_url, public=True):
            abort(HTTPStatus.BAD_REQUEST, "A valid URL is required")

        url_to_update.long_url = new_url if new_url else url_to_update.long_url
        url_to_update.title = new_title if new_title else url_to_update.title
        url_to_update.update()

        convert_referrer(url_to_update)
        url_to_update.short_url = f"{domain}{url_to_update.uuid}"
        return url_to_update, HTTPStatus.OK

    @limiter.limit("10/minute")
    @cache.cached(timeout=60)
    @jwt_required()
    def delete(self, uuid):
        user = get_jwt_identity()
        url_to_delete = Url.query.filter_by(uuid=uuid).first_or_404(description="URL Not Found")

        if url_to_delete.user_id != user:
            abort(HTTPStatus.NOT_FOUND, "URL Not Found")
        file_path = url_to_delete.qr_code
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        deleted_url = DeletedUrl(user_id=user, long_url=url_to_delete.long_url, created_at=url_to_delete.created_at)
        deleted_url.save()
        url_to_delete.delete()
        return "", HTTPStatus.NO_CONTENT


@url_namespace.route("/generate-qr-code/<string:uuid>")
class GenerateQRCode(Resource):
    """Generate a QR Code for a URL
    Accepts [GET] requests
    """
    @limiter.limit("10/minute")
    @jwt_required()
    def get(self, uuid):
        session = db.session
        user_id = get_jwt_identity()
        user = session.get(User, user_id)
        url = Url.query.filter_by(uuid=uuid).first_or_404(description="URL Not Found")
        custom_domain = user.custom_domain
        domain = custom_domain if custom_domain else request.host_url

        if url.user_id != user_id:
            abort(HTTPStatus.NOT_FOUND, "URL Not Found")

        if url.qr_code:
            file_path = url.qr_code
        else:
            file_path = f"{qr_codes_dir}\\{uuid}_qrcode.png"
            url.qr_code = file_path
            url.has_qr_code = True
            url.update()

        if os.path.exists(file_path):
            return send_file(file_path, mimetype="image/png", as_attachment=True, download_name=f"{uuid}_qrcode.png")
        else:
            img = qrcode.make(f"{domain}{uuid}?referrer=qr")
            img.save(file_path)

            return send_file(file_path, mimetype="image/png", as_attachment=True, download_name=f"{uuid}_qrcode.png")


@redirect_namespace.route("<string:short_url>")
class Redirect(Resource):
    """Redirect to the original long url
    Accepts [GET] requests
    """
    @limiter.limit("100/minute")
    def get(self, short_url):
        request_domain = request.host
        custom_domain_exists = User.query.filter_by(custom_domain=request_domain).first()

        if custom_domain_exists or request.host_url == DEFAULT_DOMAIN:
            url = Url.query.filter_by(uuid=short_url).first_or_404(description="URL Not Found")

            if url:
                long_url = url.long_url
                referrer = url.referrer

                request_referrer = request.args.get("referrer")

                url.clicks += 1

                try:
                    url_referrer_dict: dict = json.loads(referrer)

                except Exception as e:
                    abort(HTTPStatus.INTERNAL_SERVER_ERROR, e)

                if request_referrer:
                    url_referrer_dict[f"{request_referrer}"] = url_referrer_dict.get(request_referrer, 0) + 1

                else:
                    url_referrer_dict["Unknowns"] += 1

                url_referrer_str = json.dumps(url_referrer_dict)
                url.referrer = url_referrer_str
                url.update()
                return redirect(long_url)
        else:
            abort(HTTPStatus.NOT_FOUND, "URL Not Found")


@redirect_namespace.route("/hello/test/")
class Test(Resource):
    """Test Route
    Accepts [GET] requests
    Returns a success response
    """
    @limiter.limit("10/minute")
    @cache.cached(timeout=60)
    def get(self):
        return {"message": "Hello World"}, HTTPStatus.OK
