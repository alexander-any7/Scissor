import unittest
from textwrap import shorten

import shortuuid
from flask_jwt_extended import create_access_token
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash

from app_files import create_app
from app_files.config import config_dict
from app_files.models import Url, User
from app_files.utils import db

user_data = {
    "username": "testuser",
    "email": "testuser@email.com",
    "firstname": "firstname",
    "lastname": "lastname",
    "password": "password",
    "confirm_password": "password",
    "delete_custom_domain": True,
    "custom_domain": "https://example.com",
}

test_url = "https://google.com/"


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


class URLTestCase(unittest.TestCase):
    get_all_urls = "/urls/all-urls"
    get_one_url = "/urls/{uuid}"
    shorten_url = "/urls/shorten-url"
    generate_qr_code = "/generate-qr-code/{uuid}"
    redirect = "/{uuid}"

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

    def test_get_all_urls_success(self):
        user, _ = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(self.get_all_urls, headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_one_url_success(self):
        user, url = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(self.get_one_url.format(uuid=url.uuid), headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_one_url_fail_url_not_owned_by_user(self):
        _, url = create_url()
        register_data = {
            "username": "testuser2",
            "email": "testuser2@email.com",
            "firstname": "firstname",
            "lastname": "lastname",
            "password": "password",
            "confirm_password": "password",
        }
        user = create_user(custom_data=register_data)
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(self.get_one_url.format(uuid=url.uuid), headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_get_one_url_fail_unauthorized_user(self):
        _, url = create_url()
        response = self.client.get(self.get_one_url.format(uuid=url.uuid))
        self.assertEqual(response.status_code, 401)
