from http import HTTPStatus
from flask import request
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity

from app_files.models import User

user_namespace = Namespace('User', description='users namespace')



user_update_input = user_namespace.model(
    'RegisterUser', 
    {
        'firstname' : fields.String(required=True, description='An firstname for a user'),
        'lastname' : fields.String(required=True, description='An lastname for a user'),
        'custom_domain' : fields.String(required=False, description='A preferred custom domain')
    }
)

user_update_output = user_namespace.model(
    'User',
    {
        'username' : fields.String(),
        'email' : fields.String(),
        'firstname' : fields.String(),
        'lastname' : fields.String(),
        'custom_domain' : fields.String()
    }
)


@user_namespace.route('/profile')
class Users(Resource):

    @jwt_required()
    @user_namespace.expect(user_update_input)
    @user_namespace.marshal_with(user_update_output)
    def get(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        return user, HTTPStatus.OK
    


@user_namespace.route('/update-profile')
class Users(Resource):
    
    @jwt_required()
    @user_namespace.expect(user_update_input)
    @user_namespace.marshal_with(user_update_output)
    def post(self):
        user_id = get_jwt_identity()
        user = User.query.get_or_404(user_id)
        data: dict = request.get_json()
        firstname = data.get('firstname')
        lastname = data.get('lastname')
        custom_domain = data.get('custom_domain')

        user.firstname = firstname if firstname else user.firstname
        user.lastname = lastname if lastname else user.lastname

        if custom_domain:
            if custom_domain[-1] != '/':
                custom_domain = custom_domain + '/'
            user.custom_domain = custom_domain

        user.update()

        return user, HTTPStatus.OK

