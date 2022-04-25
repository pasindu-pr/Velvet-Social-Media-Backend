from .common import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'velvet',
        'USER': 'postgres',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '',
    }
}

SECRET_KEY = 'django-insecure-(8*1jgq0u7n$z%-hdp)n4nd*a+@^_vg%5lq&cp!f+f2n19+&0e'

CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200"
]

DEBUG = True

ALLOWED_HOSTS = []