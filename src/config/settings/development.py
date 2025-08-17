from .base import BASE_DIR, DEFAULT_JWT_CONFIG
from datetime import timedelta
import os
# ----------------------------------------------------------------


# --DATABASES-----------------------------------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.getenv('SQLITE_PATH', BASE_DIR.parent / 'db.sqlite3'),
    }
}
# ----------------------------------------------------------------


# ---JWT---------------------------------------------------------
SIMPLE_JWT = {
    **DEFAULT_JWT_CONFIG,
    "ACCESS_TOKEN_LIFETIME": timedelta(days=40),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=20),
}
# ----------------------------------------------------------------
