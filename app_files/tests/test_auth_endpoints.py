import unittest

from werkzeug.security import generate_password_hash

from app_files import create_app
from app_files.config import config_dict
from app_files.models import User
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


def create_user(data):
    data = data.copy()
    password_hash = generate_password_hash(data["password"])
    user = User(
        username=data["username"],
        firstname=data["firstname"],
        lastname=data["lastname"],
        email=data["email"],
        password_hash=password_hash,
    )
    user.save()


class RegisterTestCase(unittest.TestCase):
    register_data = user_data.copy()
    register_endpoint = "/auth/register"

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

    def test_user_signup_success(self):
        data = self.register_data
        response = self.client.post(self.register_endpoint, json=data)
        self.assertEqual(response.status_code, 201)

    def test_user_signup_fail_no_email(self):
        data = self.register_data.copy()
        data["email"] = "invalid"
        response = self.client.post(self.register_endpoint, json=data)
        self.assertEqual(response.status_code, 400)

    def test_user_signup_fail_password_too_short(self):
        data = self.register_data.copy()
        data["password"] = "123"
        data["confirm_password"] = "123"
        response = self.client.post(self.register_endpoint, json=data)
        self.assertEqual(response.status_code, 400)

    def test_user_signup_fail_password_do_not_match(self):
        data = self.register_data.copy()
        data["confirm_password"] = "invalid password"
        response = self.client.post(self.register_endpoint, json=data)
        self.assertEqual(response.status_code, 400)

    def test_user_signup_fail_email_exists(self):
        create_user(self.register_data)
        data = self.register_data
        data["username"] = "testuser2"
        response = self.client.post(self.register_endpoint, json=data)
        self.assertEqual(response.status_code, 409)

    def test_user_signup_fail_username_exists(self):
        create_user(self.register_data)
        data = self.register_data
        data["email"] = "testuser2@test.com"
        response = self.client.post(self.register_endpoint, json=data)
        print(response.json)
        self.assertEqual(response.status_code, 409)


class LoginTestCase(unittest.TestCase):
    login_data = {
        "username_or_email": "testuser@email.com",
        "password": "password",
    }
    login_endpoint = "/auth/login"
    register_data = user_data.copy()

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

    def test_login_success_using_email(self):
        create_user(self.register_data)
        response = self.client.post(self.login_endpoint, json=self.login_data)
        self.assertEqual(response.status_code, 200)

    def test_login_success_using_username(self):
        create_user(self.register_data)
        data = self.login_data.copy()
        data["username_or_email"] = self.register_data["username"]
        response = self.client.post(self.login_endpoint, json=self.login_data)
        self.assertEqual(response.status_code, 200)

    def test_login_fail_wrong_email(self):
        create_user(self.register_data)
        data = self.login_data.copy()
        data["username_or_email"] = "wrong@wrong.com"
        response = self.client.post(self.login_endpoint, json=data)
        self.assertEqual(response.status_code, 401)

    def test_login_fail_wrong_username(self):
        create_user(self.register_data)
        data = self.login_data.copy()
        data["username_or_email"] = "wrong_username"
        response = self.client.post(self.login_endpoint, json=data)
        self.assertEqual(response.status_code, 401)

    def test_login_fail_wrong_password(self):
        create_user(self.register_data)
        data = self.login_data.copy()
        data["password"] = "wrong_password"
        response = self.client.post(self.login_endpoint, json=data)
        self.assertEqual(response.status_code, 401)
