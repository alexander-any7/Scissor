import unittest

import shortuuid
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from api import create_app
from api.config import config_dict
from api.models import Url, User
from api.utils import db

user_data = {
    "username": "testuser",
    "email": "testuser@email.com",
    "firstname": "firstname",
    "lastname": "lastname",
    "password": "password",
    "confirm_password": "password",
    "custom_domain": "https://example.com",
}


test_url = "https://www.google.com/"


def create_user(custom_data=None):
    if custom_data:
        data = custom_data
    else:
        data = user_data.copy()
    password_hash = generate_password_hash(data["password"])
    user = User(
        username=data["username"],
        firstname=data["firstname"],
        lastname=data["lastname"],
        email=data["email"],
        password_hash=password_hash,
    )
    user.save()
    return user


def create_url():
    user = create_user()
    short_url = shortuuid.random(length=6)
    url = Url(user_id=user.id, uuid=short_url, long_url=test_url)
    url.save()
    return user, url


class UserProfileTestCase(unittest.TestCase):
    update_endpoint = "/users/update-profile"
    profile_endpoint = "/users/profile"

    def setUp(self):
        self.app = create_app(config=config_dict["testing"])
        self.app_contxt = self.app.app_context()
        self.app_contxt.push()
        self.client = self.app.test_client()
        db.create_all()

    def tearDown(self):
        db.drop_all()
        self.app_contxt.pop()
        self.app = None
        self.client = None

    def test_get_profile_success(self):
        user, _ = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(self.profile_endpoint, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_profile_fail_unauthorized_user(self):
        response = self.client.get(self.profile_endpoint)
        self.assertEqual(response.status_code, 401)

    def test_update_profile_success(self):
        user, _ = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        data = user_data.copy()
        data["firstname"] = "updated"
        response = self.client.put(self.update_endpoint, headers=headers, json=data)
        test_user = User.query.filter_by(id=user.id).first()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_user.custom_domain, f"{data['custom_domain']}/")
        self.assertEqual(test_user.firstname, "updated")

    def test_update_profile_fail_invalid_protocol_and_domain(self):
        user, _ = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        data = user_data.copy()
        data["custom_domain"] = "ht://example.com"
        response = self.client.put(self.update_endpoint, headers=headers, json=data)
        self.assertEqual(response.status_code, 400)
        data["custom_domain"] = "https://example."
        response = self.client.put(self.update_endpoint, headers=headers, json=data)
        self.assertEqual(response.status_code, 400)

    def test_remove_custom_domain_success(self):
        user, _ = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        data = user_data.copy()
        test_user = User.query.filter_by(id=user.id).first()
        self.client.put(self.update_endpoint, headers=headers, json=data)
        self.assertEqual(test_user.custom_domain, f"{data['custom_domain']}/")
        data["remove_custom_domain"] = True
        response = self.client.put(self.update_endpoint, headers=headers, json=data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(test_user.custom_domain, "")
