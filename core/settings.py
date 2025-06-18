import os
from pathlib import Path

# Ruta base
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
SECRET_KEY = 'tu-clave-secreta-aqui'  # en producción usar un .env
DEBUG = True
ALLOWED_HOSTS = []

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Tus apps ERP
]

# Middleware (procesos entre request y response)
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL config
ROOT_URLCONF = 'core.urls'

# Plantillas
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [ BASE_DIR / 'core/templates' ],
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

# WSGI (para producción)
WSGI_APPLICATION = 'core.wsgi.application'

# Base de datos PostgreSQL

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'plus_erp',
        'USER': 'postgres',
        'PASSWORD': 'bobesponja48',
        'HOST': 'localhost',  # or the IP of your server
        'PORT': '5432',
    }
}

# Password validators
AUTH_PASSWORD_VALIDATORS = [
    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator' },
    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator' },
]

# Internationalization
LANGUAGE_CODE = 'es'
TIME_ZONE = 'America/Mexico_City'

LANGUAGES = [
    ('es', 'Spanish'),
    ('en', 'English'),
    ('pl','Polish')
]

USE_I18N = True
USE_L10N = True
USE_TZ = True

# Archivos estáticos (CSS, JS)
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'apps',
]

# files upload for the user (for example PDFs)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
