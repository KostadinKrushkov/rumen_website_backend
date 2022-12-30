from project.flask.blueprints.auth.authentication_utils import hash_pass, does_hash_match_pass
from project.flask.blueprints.auth.credentials_validator import CredentialsValidator


class TestAuthenticationUtils:
    def test_hash_password_and_check_if_has_matches_original(self):
        password = "Some random password!12345"
        hashed_password = hash_pass(password)

        assert does_hash_match_pass(hashed_password, password)


class TestCredentialsValidator:
    validator = CredentialsValidator()

    def _assert_invalid_parameter(self, function_checker, parameter):
        try:
            function_checker(parameter)
        except:
            return True
        return False

    def test_validity_on_emails(self):
        valid_email = "somevalidname@gmail.com"
        self.validator.check_email(email=valid_email)

        invalid_emails = [
            'abc.def@mail.c', 'abc..def@mail.com', '.abc@mail.com', 'abc.def@mail.c',
            'abc.def@mail#archive.com', 'abc.def@mail', 'abc.def@mail..com'
        ]

        for email in invalid_emails:
            assert self._assert_invalid_parameter(self.validator.check_email, email)

    def test_validity_on_passwords(self):
        valid_password = "Somevalidpwassword123"
        self.validator.check_password(valid_password)

        invalid_passwords = 'asdf123', '1234567890', 'qwerty12345', 'qwertyASDFGH', 'ASDASDASD123123', ('asdfqwer1234' * 10)
        for password in invalid_passwords:
            assert self._assert_invalid_parameter(self.validator.check_password, password)

