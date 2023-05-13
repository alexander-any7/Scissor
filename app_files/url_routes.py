import os
import json
# import redis
import qrcode
import validators
import shortuuid
from http import HTTPStatus
from flask import request, redirect, send_file
from flask_restx import Namespace, Resource, fields, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from app_files.models import Url, User
from decouple import config

DEFAULT_DOMAIN = config('DEFAULT_DOMAIN')

# Get the directory of the script file
script_dir = os.path.dirname(os.path.abspath(__file__))


url_namespace = Namespace('Url', description='urls namespace')
redirect_namespace = Namespace('Redirect', description='redirect namespace')

# redis_client = redis.Redis(host='localhost', port=5000, db=0)

url_input = url_namespace.model(
    'Url', 
    {
        'url' : fields.String(required=True, description='url to shorten'),
    }
)

url_input_update = url_namespace.model(
    'Url', 
    {
        'url' : fields.String(required=True, description='url to shorten'),
        "use_default_domain" : fields.Boolean(description="To use default domain", default=False) 
    }
)

url_output = url_namespace.model(
    'Url',
    {
        "short_url": fields.String(),
        "long_url": fields.String()
    }
)


@url_namespace.route('/shorten_url')
class Urls(Resource):
    
    @jwt_required()
    @url_namespace.expect(url_input)
    @url_namespace.marshal_with(url_output)
    def post(self):

        user = get_jwt_identity()
        data: dict = request.get_json()
        url = data.get('url')
        user_domain = User.query.filter_by(id=user).first().custom_domain

        domain = f'{user_domain}' if user_domain else request.host_url
        
        if not url or not validators.url(url, public=True):
            abort(HTTPStatus.BAD_REQUEST, 'A valid URL is required')

        existing_urls = Url.query.filter_by(long_url=url).all()

        for s_url in existing_urls:
            if s_url.user_id == user:
                s_url.short_url = f'{domain}{s_url.uuid}'
                return s_url, HTTPStatus.OK
        
        short_url = shortuuid.random(length=6)

        new_url = Url(user_id=user, uuid=short_url, long_url=url)
        new_url.referrer = json.dumps({"Unknowns":0})
        new_url.save()

        new_url.short_url = f'{domain}{short_url}'
        return new_url, HTTPStatus.CREATED


@url_namespace.route('/all_urls')
class Urls(Resource):
    
    @jwt_required()
    @url_namespace.marshal_list_with(url_output)
    def get(self):
        user = get_jwt_identity()
        user_domain = User.query.filter_by(id=user).first().custom_domain
        domain = f'{user_domain}' if user_domain else request.host_url
        urls = Url.query.filter_by(user_id=user).all()        
        for url in urls:
            url.short_url = f'{domain}{url.uuid}'
        return urls, HTTPStatus.OK
    

@url_namespace.route('/<string:uuid>')
class Urls(Resource):

    @jwt_required()
    @url_namespace.marshal_list_with(url_output)
    def get(self, uuid):
        user = get_jwt_identity()
        user_domain = User.query.filter_by(id=user).first().custom_domain
        domain = f'{user_domain}' if user_domain else request.host_url
        url = Url.query.filter_by(uuid=uuid).first_or_404(description='URL Not Found')

        if url.user_id != user:
            abort(HTTPStatus.NOT_FOUND, 'URL Not Found')
        
        url.short_url = f'{domain}{url.uuid}'
        return url, HTTPStatus.OK
    
    @jwt_required()
    @url_namespace.marshal_list_with(url_output)
    @url_namespace.expect(url_input_update)
    def put(self, uuid):
        user = get_jwt_identity()
        user_domain = User.query.filter_by(id=user).first().custom_domain
        domain = f'{user_domain}' if user_domain else request.host_url
        url_to_update = Url.query.filter_by(uuid=uuid).first_or_404(description='URL Not Found')

        if url_to_update.user_id != user:
            abort(HTTPStatus.NOT_FOUND, 'URL Not Found')

        data: dict = request.get_json()
        new_url = data.get('url')

        url_to_update.long_url = new_url if new_url else url_to_update.long_url
        url_to_update.update()

        url_to_update.short_url = f'{domain}{url_to_update.uuid}'

        return url_to_update, HTTPStatus.OK


    @jwt_required()
    def delete(self, uuid):
        user = get_jwt_identity()
        url_to_delete = Url.query.filter_by(uuid=uuid).first_or_404(description='URL Not Found')

        if url_to_delete.user_id != user:
            abort(HTTPStatus.NOT_FOUND, 'URL Not Found')
        
        url_to_delete.delete()
        return "", HTTPStatus.NO_CONTENT
    

@url_namespace.route('/generate-qr-code/<string:uuid>')
class Urls(Resource):
    
    @jwt_required()
    def get(self, uuid):
        user_id = get_jwt_identity()
        url = Url.query.filter_by(uuid=uuid).first_or_404(description="URL Not Found")
        user = User.query.get_or_404(user_id)
        custom_domain = user.custom_domain
        domain = custom_domain if custom_domain else request.host_url

        if url.user_id != user_id:
            abort(HTTPStatus.NOT_FOUND, 'URL Not Found')
        
        file_path = os.path.join(script_dir, 'qr_codes', f'{uuid}_qrcode.png')
        
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/png', as_attachment=True, download_name=f'{uuid}_qrcode.png')
        else:
            img = qrcode.make(f'{domain}{uuid}?referrer=qr')
            img.save(file_path)

            return send_file(file_path, mimetype='image/png', as_attachment=True, download_name=f'{uuid}_qrcode.png')
        

@redirect_namespace.route('<string:short_url>')
class Urls(Resource):
    def get(self, short_url):
        request_domain = request.host
        custom_domain_exists = User.query.filter_by(custom_domain=request_domain).first()

        if custom_domain_exists or request.host_url == DEFAULT_DOMAIN:
                         
            url = Url.query.filter_by(uuid=short_url).first_or_404(description="URL Not Found")

            if url:
                long_url = url.long_url
                referrer = url.referrer

                request_referrer = request.referrer

                url.clicks += 1

                try:
                    url_referrer_dict: dict= json.loads(referrer)
                    
                except Exception as e:
                    abort(HTTPStatus.INTERNAL_SERVER_ERROR, e)

                if request_referrer:
                    url_referrer_dict[f"{request_referrer}"] = url_referrer_dict.get(request_referrer, 0) + 1
                    url_referrer_str = json.dumps(url_referrer_dict)

                else:
                    url_referrer_dict["Unknowns"] += 1
                    url_referrer_str = json.dumps(url_referrer_dict)


                url.referrer = url_referrer_str
                url.update()
                return redirect(long_url)
        else:
            abort(HTTPStatus.NOT_FOUND, "URL Not Found")
