import datetime
import os

BACKEND_EMAIL = os.environ.get('BACKEND_EMAIL')
BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL')
BACKEND_EMAIL_PASS = os.environ.get('BACKEND_EMAIL_PASS')
DB_USER = os.environ.get('DB_USER')
DB_PASSWORD = os.environ.get('DB_PASSWORD')
DB_SERVER = os.environ.get('DB_SERVER')
DB_NAME = os.environ.get('DB_NAME')
TEST_DB_NAME = os.environ.get('TEST_DB_NAME')
DB_DRIVER = os.environ.get('DB_DRIVER')
CERT_PATH = os.environ.get('CERT_PATH')
CERT_KEY_PATH = os.environ.get('CERT_KEY_PATH')
FULL_SECRET_KEY = os.environ.get('SECRET_KEY')
# TEST_SECRET_KEY = bytes(FULL_SECRET_KEY)
SECRET_KEY = b'52921dbb69f4d358b3c9dddb1d31f036e2222c055589a1101acaa4ec700cbc23'
VERIFY_RECAPTCHA_URL = 'https://www.google.com/recaptcha/api/siteverify'  # TODO create them as env parameters
RECAPTCHA_SECRET_KEY = '6Lfu-WYkAAAAABlDwJ_xyjFx_B6C7hBUSsZYTvhT'
SMTP_REQUESTS_LIMIT = '200/day'


EXPIRATION_DATETIME_DELTA = datetime.timedelta(days=31, seconds=3)
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=31)  # The length of a user log in session
