import os
from pathlib import Path
from core.readApps import APPS_FOLDER, APPS_NAME
from core.updateAllTheFilesOfTheApps import *
# load the variables in the file .env
from dotenv import load_dotenv
load_dotenv()

print("""
    -----------------------------------------------------------------
    PLUS ERP
    Power By {ED} Software Developer
    The server is run
    -----------------------------------------------------------------
""""")

#------------------------------------------------------run server---------------------------------------------
# Ruta base
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
secret_key = os.getenv('SECRET_KEY')
SECRET_KEY = secret_key if secret_key else 'tu-clave-secreta-aqui'
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
    'database',
    'core'
]+APPS_NAME #your apps ERP


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
        'DIRS': [ 
            #this is for load the templates of the web ERP
            BASE_DIR / 'core/templates' , 

            #this is for load all the templates(views) of all the apps
            *[(folder / 'views') for folder in APPS_FOLDER]
        ],
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

# read the variables
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_pass = os.getenv('DB_PASS')
db_name = os.getenv('DB_NAME')
db_port = os.getenv('DB_PORT')

# Base de datos PostgreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': db_name,
        'USER': db_user,
        'PASSWORD': db_pass,
        'HOST': db_host,
        'PORT': db_port,
        'OPTIONS': {
            'options': '-c search_path=customer,public',
        },
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

#setting login
AUTH_USER_MODEL = 'core.CustomUser' #this is the model that need the login of the user
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

# files upload for the user (for example PDFs)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
