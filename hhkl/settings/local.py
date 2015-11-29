from .base import *

DEBUG = True

TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS += (
    'debug_toolbar',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'hhkl',
        'USER': 'hhkl',
        'PASSWORD': 'hhkl',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}