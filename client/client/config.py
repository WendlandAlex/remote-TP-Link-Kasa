from os import environ, path
from dotenv import load_dotenv
import random

basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

class Config:
    FLASK_ENV = environ.get('FLASK_ENV', 'dev')
    TESTING = environ.get('TESTING', True)
    SECRET_KEY = environ.get('SECRET_KEY', random.randbytes(128))
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    PYOTP_SECRET = environ.get('PYOTP_SECRET')
    