import ssl
import smtplib
import datetime
import jwt
from email.message import EmailMessage
from datetime import datetime, timedelta
from decouple import config

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
secret_key = config('SECRET_KEY')
DEFAULT_DOMAIN = config('DEFAULT_DOMAIN')


class CredentialsException(Exception):
    pass


class MailService:

    @staticmethod
    def send_reset_mail(email: str, token: str, uuid: str) -> bool:
        """
        Send two factor authentication code to hte email address in the kwargs

        """
        sender_email = config('EMAIL_SENDER')
        sender_password = config('EMAIL_PASSWORD')

        if not (sender_email and sender_password):
            raise ValueError(
                "Sender email and password not found in environment variables")

        subject = "Password reset"
        body = f"""
                We have received a request to reset your password.
                Ignore this message if you didn't make the request or click the link below to reset your password.
                This link is only active for 10 minutes.
                {DEFAULT_DOMAIN}auth/password-reset/{token}/{uuid}/confirm

                From the Scissor team 
            """

        message = EmailMessage()
        message["subject"] = subject
        message["From"] = sender_email
        message["To"] = email
        message.set_content(body)

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", port=465, context=context) as server:
                server.login(sender_email, sender_password)
                server.send_message(message)
        except smtplib.SMTPAuthenticationError:
            raise ValueError("Invalid sender email or password")

        except Exception as e:
            raise ValueError("Failed to send email") from e

        return True


class TokenService:

    @staticmethod
    def create_password_reset_token(user_id: str) -> str:
        """
        Generate a token for a user.
        :param user_id: The id of a user

        """
        expires_at = datetime.utcnow() + timedelta(minutes=10)

        payload = {
            "user_id": user_id,
            "expires_at": expires_at.isoformat(),
        }

        token = jwt.encode(payload, secret_key, algorithm='HS256')
        return token

    @staticmethod
    def validate_password_reset_token(token: str, user_id: int) -> bool:
        try:
            payload = jwt.decode(token, secret_key, algorithms=['HS256'])
            payload_user_id: str = payload.get('user_id')
            expires_at = payload.get('expires_at')

            try:
                expires_at_dt = datetime.fromisoformat(expires_at).timestamp()

            except Exception as e:
                expires_at_dt = 0

            if payload_user_id is None or expires_at is None or expires_at_dt < datetime.utcnow().timestamp() or payload_user_id != user_id:
                return False

            return True

        except jwt.exceptions.DecodeError as e:
            raise e

        except jwt.exceptions.ExpiredSignatureError as e:
            raise e

        except Exception as e:
            raise e
