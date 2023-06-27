import os
from datetime import timedelta

from decouple import config

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
QR_CODE_DIRECTORY = f"{BASE_DIR}/qr_codes"

if not os.path.exists(QR_CODE_DIRECTORY):
    os.makedirs(QR_CODE_DIRECTORY)

uri = config("DATABASE_URL")  # or other relevant config var
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)


class Config:
    SECRET_KEY = config("SECRET_KEY", "secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(minutes=60)
    JWT_SECRET_KEY = config("JWT_SECRET_KEY")
    ALGORITHM = config("ALGORITHM")
    ACCESS_TOKEN_EXPIRES_MINUTES = config("ACCESS_TOKEN_EXPIRES_MINUTES")
    DEFAULT_DOMAIN = config("DEFAULT_DOMAIN")
    CACHE_DEFAULT_TIMEOUT = config("CACHE_DEFAULT_TIMEOUT")


class DevConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(PARENT_DIR, "scissor.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DEBUG = config("FLASK_DEBUG", cast=bool)


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DEBUG = config("FLASK_DEBUG", cast=bool)


config_dict = {
    "dev": DevConfig,
    "testing": TestConfig,
    "production": ProdConfig,
}
