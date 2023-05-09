import datetime
import os


class Config:
    DEBUG = True
    DEVELOPMENT_FLAG = False
    STATIC_IP_ADDRESS = os.environ.get('STATIC_ADDRESS')
    BACKEND_EMAIL = os.environ.get('BACKEND_EMAIL')
    BUSINESS_EMAIL = os.environ.get('BUSINESS_EMAIL')
    BACKEND_EMAIL_PASS = os.environ.get('BACKEND_EMAIL_PASS')
    DB_USER = 'sa' if DEVELOPMENT_FLAG else os.environ.get('DB_USER')
    DB_SERVER = 'localhost, 1433' if DEVELOPMENT_FLAG else os.environ.get('DB_SERVER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_NAME = os.environ.get('DB_NAME')
    TEST_DB_NAME = os.environ.get('TEST_DB_NAME')
    DB_DRIVER = os.environ.get('DB_DRIVER')
    CERT_PATH = os.environ.get('CERT_PATH')
    CERT_KEY_PATH = os.environ.get('CERT_KEY_PATH')
    FULL_SECRET_KEY = os.environ.get('SECRET_KEY')
    SECRET_KEY = bytes(FULL_SECRET_KEY, encoding='utf-8')

    VERIFY_RECAPTCHA_URL = os.environ.get('VERIFY_RECAPTCHA_URL')
    RECAPTCHA_SECRET_KEY = os.environ.get('RECAPTCHA_SECRET_KEY')
    SMTP_REQUESTS_LIMIT = os.environ.get('SMTP_REQUESTS_LIMIT')

    EXPIRATION_DATETIME_DELTA = datetime.timedelta(days=31, seconds=3)
    PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=31)  # The length of a user log in session
    REMEMBER_COOKIE_DURATION = PERMANENT_SESSION_LIFETIME
    NUM_PICTURES_TO_EXTEND_LOAD = 18
    GMAIL_PORT = 465

    SESSION_COOKIE_SECURE = True
    SESSION_PERMANENT = True
    REMEMBER_COOKIE_SECURE = True
    HOME_PICTURES_PATH = 'project/flask/blueprints/picture/home_displayed_pictures.txt' if DEVELOPMENT_FLAG else 'home_displayed_pictures.txt'
    TEST_HOME_PICTURES_PATH = r'/test_home_displayed_pictures.txt'
    TESTING_FILES = (TEST_HOME_PICTURES_PATH, )
