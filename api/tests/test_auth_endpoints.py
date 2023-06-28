import unittest

from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash

from api import create_app
from api.config import config_dict
from api.models import User
from api.utils import TokenService, db

user_data = {
    "username": "testuser",
    "email": "testuser@email.com",
    "firstname": None,
    "lastname": None,
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
    return user


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


class PasswordResetTestCase(unittest.TestCase):
    password_reset_request = "/auth/password-reset-request"
    reset_password = "/auth/reset-password"
    password_reset_confirm = "/auth/password-reset/{token}/{uuid}/confirm"
    username = {"username_or_email": user_data["username"]}
    email = {"username_or_email": user_data["email"]}

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

    def test_send_password_reset_email_success_using_username(self):
        create_user(user_data)
        response = self.client.post(self.password_reset_request, json=self.username)
        self.assertEqual(response.status_code, 200)

    def test_send_password_reset_email_success_using_email(self):
        create_user(user_data)
        response = self.client.post(self.password_reset_request, json=self.email)
        self.assertEqual(response.status_code, 200)

    def test_send_password_reset_email_fail_user_not_found(self):
        response = self.client.post(self.password_reset_request, json=self.email)
        self.assertEqual(response.status_code, 406)

    def test_reset_password_confirm_success(self):
        data = {"password_1": "newpassword", "password_2": "newpassword"}
        user = create_user(user_data)
        user_id = str(user.id)
        token = TokenService.create_password_reset_token(user_id)
        response = self.client.post(self.password_reset_confirm.format(token=token, uuid=user_id), json=data)
        self.assertEqual(response.status_code, 200)

    def test_reset_password_success_logged_in_user(self):
        data = {"current_password": "password", "new_password_1": "newpassword", "new_password_2": "newpassword"}
        user = create_user(user_data)
        token = create_access_token(identity=user.id)
        headers = {"Authorization": f"Bearer {token}"}
        response = self.client.post(self.reset_password, json=data, headers=headers)
        print(response.json)
        self.assertEqual(response.status_code, 200)
