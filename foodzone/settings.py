from pathlib import Path
import os
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
TIME_ZONE = "Asia/Kolkata"
USE_TZ = True


#True

# Load environment variables from .env file
load_dotenv(dotenv_path=BASE_DIR / ".env")
load_dotenv(dotenv_path=BASE_DIR / "foodzone"/".env")

SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "fallback-secret-key")
DEBUG = os.getenv("DEBUG", "False") == "True"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    
    # Your apps
    #'myapp',
    'myapp.apps.MyappConfig',

    # Third-party apps
    'crispy_forms',
    'crispy_bootstrap5',
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
   
]

SITE_ID = 1

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

ACCOUNT_EMAIL_VERIFICATION = 'none'
ACCOUNT_EMAIL_REQUIRED = False
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'APP': {
            'client_id': os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_KEY"),
            'secret': os.getenv("SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET"),
        }
    }
}

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'allauth.account.middleware.AccountMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    
]

ROOT_URLCONF = 'foodzone.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / "templates"],
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



WSGI_APPLICATION = 'foodzone.wsgi.application'
#local db
'''
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv("DATABASE_NAME"),
        'USER': os.getenv("DATABASE_USER"),
        'PASSWORD': os.getenv("DATABASE_PASSWORD"),
        'HOST': os.getenv("DATABASE_HOST"),
        'PORT': os.getenv("DATABASE_PORT"),
    }
}
'''
# render postgresql database live

import os
import dj_database_url

DATABASE_URL = os.getenv("DATABASE_URL")

# Ensure DATABASE_URL is set
if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL)
    }
else:
    raise ValueError("DATABASE_URL is not set in the environment variables")




AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'

ALLOWED_HOSTS=['*']
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / "static"]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

raw_paypal_mode = os.getenv("PAYPAL_MODE", "sandbox")
# Strip out any inline comment: split on '#' and take the first part, then remove extra spaces
PAYPAL_MODE = raw_paypal_mode.split('#')[0].strip()

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET")

#print("PAYPAL_MODE:", os.getenv("PAYPAL_MODE"))
# # settings.py (temporarily)
# PAYPAL_MODE = 'sandbox'
# PAYPAL_CLIENT_ID = 'AZvVzdXPjjQABG_O7tKAB37AZjJlqa9CSGuckPqZHnrYvJ8rJZmZjbW5C7gbRw1yyx5hp7NdMJWJD-An'
# PAYPAL_CLIENT_SECRET = 'EJDVrrHymaUqsEXDkF7o548p7YaJ8fxrOGGRGQK5JUigj0OHUlCSSG2mfmAfwf704EDtm0JZ5lqGZKmq'

# In settings.py
# print(f"PayPal Mode: {PAYPAL_MODE}")
# print(f"PayPal Client ID: {'****' + PAYPAL_CLIENT_ID[-4:] if PAYPAL_CLIENT_ID else 'Not set'}")
# settings.py
# print("\nPayPal Configuration:")
# print(f"Mode: {PAYPAL_MODE}")
# print(f"Client ID: {'****' + PAYPAL_CLIENT_ID[-4:] if PAYPAL_CLIENT_ID else 'MISSING'}")
# print(f"Client Secret: {'****' + PAYPAL_CLIENT_SECRET[-4:] if PAYPAL_CLIENT_SECRET else 'MISSING'}\n")

# settings.py
# print("\nPayPal Configuration:")
# print(f"Mode: {PAYPAL_MODE}")
# print(f"Client ID: {'****' + PAYPAL_CLIENT_ID[-4:] if PAYPAL_CLIENT_ID else 'MISSING'}")
# print(f"Secret: {'****' + PAYPAL_CLIENT_SECRET[-4:] if PAYPAL_CLIENT_SECRET else 'MISSING'}\n")
# Crispy Forms Bootstrap 5
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"
