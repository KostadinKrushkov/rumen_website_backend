import datetime
import jwt
from project.settings import Config
from flask_login import UserMixin


class User(UserMixin):
    def __init__(self, email, username, password, is_admin=False, is_verified=False, id=None):
        self.email = email
        self.password = password
        self.username = username
        self.registered_on = datetime.datetime.now()
        self.is_admin = is_admin == 1
        self.is_verified = is_verified == 1
        self.id = str(id) if id else None

    def get_id(self):
        return self.id

    @classmethod
    def from_dto(cls, user_dto):
        return cls(email=user_dto.email,
                   username=user_dto.username,
                   password=user_dto.password,
                   is_admin=user_dto.is_admin,
                   is_verified=user_dto.is_verified,
                   id=user_dto.id)

    @staticmethod
    def encode_auth_token(user_id):
        """Generates the Auth Token"""
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + Config.EXPIRATION_DATETIME_DELTA,
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                Config.SECRET_KEY,
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """Validates the auth token"""
        payload = jwt.decode(auth_token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload['sub']
