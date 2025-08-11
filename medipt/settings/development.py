from .base import *  # noqa: F403, F401


# Environment indicator
ENVIRONMENT = 'development'
DEBUG = True
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "*"]

# # SQLite for development (simple setup)
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#         'OPTIONS': {
#             'timeout': 20,
#         }
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME', default='medipt_dev'),
        'USER': env('DB_USER', default='postgres'),
        'PASSWORD': env('DB_PASSWORD', default='postgres'),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}

# This prevents Redis connection errors during development
try:
    import redis
    redis_client = redis.Redis.from_url(env("REDIS_URL", default="redis://127.0.0.1:6379/1"))
    redis_client.ping()
    
    # Redis is available, use it
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": env("REDIS_URL", default="redis://127.0.0.1:6379/1"),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
            },
            "KEY_PREFIX": "medipt_dev_cache",
            "TIMEOUT": 300,
        }
    }
except (ImportError, redis.exceptions.ConnectionError):
    # Redis not available, use dummy cache
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        }
    }


# Use database sessions in development (more reliable than cache)
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_SECURE = False  # Allow cookies over HTTP in development
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"

# CSRF settings for development
CSRF_COOKIE_SECURE = False  # Allow CSRF cookies over HTTP in development
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3001",  # Additional ports for development
    "http://127.0.0.1:8000",  # Django dev server
]

# More permissive CORS for development
CORS_ALLOW_ALL_ORIGINS = True  # Allow all origins in development
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    "http://localhost:3001",
]


# Console backend for development (prints emails to console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Alternative: Use MailHog for development email testing
# EMAIL_HOST = "localhost"
# EMAIL_PORT = 1025
# EMAIL_USE_TLS = False
# EMAIL_HOST_USER = ""
# EMAIL_HOST_PASSWORD = ""

DEFAULT_FROM_EMAIL = "medipt-dev@example.com"

# OR use Cloudinary with development folder (RECOMMENDED)
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
CLOUDINARY_STORAGE.update({
    'OPTIONS': {
        'folder': 'development',  # Separate folder for dev uploads
        'quality': 'auto:low',    # Lower quality for faster uploads
        'format': 'auto',
    }
})

# Simple static files setup for development
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"


# Add development-specific apps
DEV_APPS = [
    'debug_toolbar',
    'django_browser_reload',
]

# Check if debug toolbar is installed before adding
try:
    import debug_toolbar
    INSTALLED_APPS += DEV_APPS
except ImportError:
    print("Debug toolbar not installed. Install with: pip install django-debug-toolbar")


if 'debug_toolbar' in INSTALLED_APPS:
    # Add debug toolbar middleware
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
    
    # Add browser reload middleware
    if 'django_browser_reload' in INSTALLED_APPS:
        MIDDLEWARE.append('django_browser_reload.middleware.BrowserReloadMiddleware')
    
    # Internal IPs for debug toolbar
    import socket
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[: ip.rfind(".")] + ".1" for ip in ips] + [
        "127.0.0.1",
        "10.0.2.2",
    ]
    
    # Debug toolbar panels
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
        'debug_toolbar.panels.profiling.ProfilingPanel',
    ]


# Execute tasks synchronously in development (easier debugging)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True


# More verbose logging for development
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "{log_color}{levelname} {asctime} {module} {message}",
            "style": "{",
        } if "colorlog" in locals() else {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "colored" if "colorlog" in locals() else "simple",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": BASE_DIR / "logs" / "development.log",
            "maxBytes": 1024 * 1024 * 5,  # 5 MB
            "backupCount": 3,
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "medipt": {
            "handlers": ["console", "file"],
            "level": "DEBUG",  # More verbose for your app
            "propagate": False,
        },
        "django.db.backends": {
            "handlers": ["console"],
            "level": "DEBUG",  # Show SQL queries in development
            "propagate": False,
        },
        # Silence noisy loggers
        "django.utils.autoreload": {
            "level": "INFO",
            "propagate": False,
        },
    },
}


# Add browsable API for development
REST_FRAMEWORK.update({
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",  # Enable browsable API
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "1000/hour",  # More permissive rates for development
        "user": "5000/hour",
    },
    "PAGE_SIZE": 20,  # Reasonable page size for development
})


# Longer token lifetimes for easier development
SIMPLE_JWT.update({
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),  # 1 hour for easier testing
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
})

# Disable SSL redirects in development
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False
SECURE_PROXY_SSL_HEADER = None

# More permissive file upload settings for development
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB


# Create logs directory if it doesn't exist
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

FRONTEND_URL='http://localhost:3000'

# Print useful development information
print("🚀 Running in DEVELOPMENT mode")
print(f"📁 Database: {DATABASES['default']['ENGINE'].split('.')[-1]}")
print(f"💾 Cache: {'Redis' if 'redis' in CACHES['default']['BACKEND'] else 'Dummy'}")
print(f"📧 Email: {EMAIL_BACKEND.split('.')[-1]}")
print(f"📁 Storage: {'Cloudinary' if 'cloudinary' in DEFAULT_FILE_STORAGE else 'Local'}")
