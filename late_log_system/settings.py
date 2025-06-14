from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

LOGIN_URL = '/login/'  # Redirect to the login page if the user is not authenticated

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-6iu^t+n$rf9q2@06^ii_u4if-u48b+9aoi6=j_qxf@n1c22l4d'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['late-log-app.onrender.com', 'localhost', '127.0.0.1']
CSRF_TRUSTED_ORIGINS = [
    'http://192.168.254.128',
]
  



# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
     # Add your app here:
    'logs',  # Add the 'logs' app to the list
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'late_log_system.urls'


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'logs' / 'templates'],  # This path should point to your templates folder
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




WSGI_APPLICATION = 'late_log_system.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # Use PostgreSQL
        'NAME': os.getenv('DB_NAME', 'postgresql_latelogcnhs'),  # Database name
        'USER': os.getenv('DB_USER', 'postgresql_latelogcnhs_user'),  # Database user
        'PASSWORD': os.getenv('DB_PASSWORD', 'uhjdsRHzAVJ73bK3GaSPK0sG177jjvUH'),  # Database password
        'HOST': os.getenv('DB_HOST', 'dpg-d14jg8bipnbc73ffe060-a.oregon-postgres.render.com'),  # Database host
        'PORT': os.getenv('DB_PORT', '5432'),  # PostgreSQL default port
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Manila'

USE_I18N = True

USE_TZ = True

CSRF_COOKIE_SECURE = False  # Set to True if you're using HTTPS
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'  # Options: 'Strict', 'Lax', or 'None'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Directory to collect static files during deployment

STATICFILES_DIRS = [
    BASE_DIR / 'static',  # Make sure your static files are in a directory like this
]

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # Directory for storing user-uploaded files
X_FRAME_OPTIONS = 'ALLOWALL'
