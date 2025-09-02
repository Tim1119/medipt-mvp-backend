from .base import * 


# CORS Configuration
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", default="").split()
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True


EMAIL_HOST = env("DEV_EMAIL_HOST")
EMAIL_PORT = env("DEV_EMAIL_PORT")
EMAIL_HOST_USER = env("DEV_EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("DEV_EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")
EMAIL_USE_TLS = True


FRONTEND = ""

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DEV_DB_NAME'),
        'USER': env('DEV_DB_USER'),
        'PASSWORD': env('DEV_DB_PASSWORD'),
        'HOST': env('DEV_DB_HOST'),
        'PORT': env('DEV_DB_PORT'),
    }
}
