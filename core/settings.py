import os
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import timedelta
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY=os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS=[
    "127.0.0.1",
    "10.0.2.2",
]
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://10.0.2.2:8000",
]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'channels',

    'apps.accounts.apps.AccountsConfig',
    'apps.logistics.apps.LogisticsConfig',
    'apps.payments.apps.PaymentsConfig',
    'apps.messaging.apps.MessagingConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=20),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",

    "AUTH_HEADER_TYPES": ("Token",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "uid",
    "USER_ID_CLAIM": "uid",
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    )
}

ASGI_APPLICATION = 'core.asgi.application'


ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        
    },
    'accounts': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME':'expa_accounts',
        'USER':'postgres',
        'PASSWORD':'1234',
        'HOST':'localhost',
        'PORT': '5432'
    },
    'logistics': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME':'expa_logistics',
        'USER':'postgres',
        'PASSWORD':'1234',
        'HOST':'localhost',
        'PORT': '5432'
    },
    'payments': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME':'expa_payments',
        'USER':'postgres',
        'PASSWORD':'1234',
        'HOST':'localhost',
        'PORT': '5432'
    },
    'messaging': {
        'ENGINE':'django.db.backends.postgresql',
        'NAME':'expa_messaging',
        'USER':'postgres',
        'PASSWORD':'1234',
        'HOST':'localhost',
        'PORT': '5432'
    }
}


DATABASE_ROUTERS = [
    "routers.db_routers.AuthRouter",
    "routers.db_routers.Logistics",
    "routers.db_routers.Payments",
    "routers.db_routers.Messaging",
]


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, "static")

MEDIA_URL = "media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = "accounts.User"
