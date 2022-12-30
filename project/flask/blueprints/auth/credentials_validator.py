from email_validator import validate_email
from password_validator import PasswordValidator
from username_validator import UsernameValidator


class CredentialsValidator:
    def __init__(self):
        self.password_schema = PasswordValidator()
        self.username_validator = UsernameValidator()
        self.password_schema.min(10).max(100).has().uppercase().has().lowercase().has().digits()

    def validate_user_credentials(self, user_json):
        email = user_json.get('email')
        password = user_json.get('password')
        username = user_json.get('username')

        if not all((email, password, username)):
            return False

        try:
            self.check_email(email)
            self.check_password(password)
            self.check_username(username)
        except Exception:
            return False
        return True

    def check_email(self, email):
        validated_email = validate_email(email)
        if not validated_email.email:
            raise Exception("Invalid email!")

    def check_password(self, password):
        if not self.password_schema.validate(password):
            raise Exception("Invalid password!")

    def check_username(self, username):
        self.username_validator.validate_all(username)
