import os
import unittest

import shortuuid
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from api import create_app
from api.config import config_dict
from api.models import DeletedUrl, Url, User
from api.utils import db

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

second_user_data = {
    "username": "testuser2",
    "email": "testuser2@email.com",
    "firstname": "firstname",
    "lastname": "lastname",
    "password": "password",
    "confirm_password": "password",
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


class URLTestCase(unittest.TestCase):
    get_all_urls = "/urls/all-urls"
    one_url = "/urls/{uuid}"
    shorten_url = "/urls/shorten-url"
    generate_qr_code = "/urls/generate-qr-code/{uuid}"
    redirect = "/{uuid}"
    deleted_urls = "urls/deleted-urls"
    restore_url = "/urls/restore-url/{id}"
    update_url_data = {"url": "https://web.facebook.com/"}

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
        response = self.client.get(self.one_url.format(uuid=url.uuid), headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_get_one_url_fail_url_not_owned_by_user(self):
        _, url = create_url()
        register_data = second_user_data.copy()
        user = create_user(custom_data=register_data)
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(self.one_url.format(uuid=url.uuid), headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_get_one_url_fail_unauthorized_user(self):
        _, url = create_url()
        response = self.client.get(self.one_url.format(uuid=url.uuid))
        self.assertEqual(response.status_code, 401)

    def test_update_url_success(self):
        user, url = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.put(self.one_url.format(uuid=url.uuid), json=self.update_url_data, headers=headers)
        self.assertEqual(response.status_code, 200)
        test_url = Url.query.filter_by(uuid=url.uuid).first()
        self.assertEqual(test_url.long_url, self.update_url_data["url"])

    def test_update_url_fail_url_not_found(self):
        user, _ = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.put(
            self.one_url.format(uuid=shortuuid.random(length=6)), json=self.update_url_data, headers=headers
        )
        self.assertEqual(response.status_code, 404)

    def test_update_url_fail_url_not_owned_by_user(self):
        _, url = create_url()
        register_data = second_user_data.copy()
        user = create_user(custom_data=register_data)
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.put(self.one_url.format(uuid=url.uuid), json=self.update_url_data, headers=headers)
        self.assertEqual(response.status_code, 404)

    def test_delete_url_success(self):
        user, url = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.delete(self.one_url.format(uuid=url.uuid), headers=headers)
        self.assertEqual(response.status_code, 204)

    def test_generate_qrcode_success(self):
        user, url = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.get(self.generate_qr_code.format(uuid=url.uuid), headers=headers)
        print("here", response.json)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(os.path.exists(url.qr_code), True)

    def test_get_deleted_urls_success(self):
        user, url = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        self.client.delete(self.one_url.format(uuid=url.uuid), headers=headers)
        deleted_urls = DeletedUrl.query.all()
        response = self.client.get(self.deleted_urls, headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(deleted_urls), 1)

    def test_restore_url_success(self):
        user, url = create_url()
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        self.client.delete(self.one_url.format(uuid=url.uuid), headers=headers)
        response = self.client.get(self.restore_url.format(id=url.id), headers=headers)
        deleted_urls = DeletedUrl.query.all()
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(deleted_urls), 0)
