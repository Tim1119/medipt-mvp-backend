from .base import * 


# CORS Configuration
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", default="").split()
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = True


# Email Configuration (base - override in environment files)
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = env("DEVELOPMENT_EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = env("DVELOPMENT_EMAIL_PORT", default=587, cast=int)
EMAIL_HOST_USER = env("DEVELOPMENT_EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = env("DEVELOPMENT_EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL")


FRONTEND = ""