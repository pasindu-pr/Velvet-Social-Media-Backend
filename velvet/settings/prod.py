from .common import *
import dj_database_url
import os

DEBUG = os.environ.get("DEBUG") == 'TRUE' 
CSRF_TRUSTED_ORIGINS = [os.getenv('HOST_NAME')]
SECRET_KEY = os.getenv("SECRET_KEY")

DATABASES = {
    'default' : dj_database_url.config()
} 

CORS_ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_URL")
]

ALLOWED_HOSTS = [os.getenv("FRONTEND_URL")]