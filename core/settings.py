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

#character of the ERP
FIELD_ENCRYPTION_KEY = os.environ.get('FIELD_ENCRYPTION_KEY').encode()
TYPE_VERSION = os.getenv('TYPE_VERSION', 'DESKTOP')
PLUS_URL=os.getenv('PLUS_URL', 'localhost')


TERMS_VERSION = "1.0.1" #This is the version of the terms and conditions in our web

#------------------------------------------------------run server---------------------------------------------
# Ruta base
BASE_DIR = Path(__file__).resolve().parent.parent

# Seguridad
secret_key = os.getenv('SECRET_KEY')
SECRET_KEY = secret_key if secret_key else 'your_secret_key'

debug=(TYPE_VERSION == 'DESKTOP')
DEBUG = debug
MINIFY_HTML_DEBUG = True#debug

ALLOWED_HOSTS = []

# Apps instaladas
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'database',
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
    
    #this is for know if the subscription of the user expired
    'core.middleware.SubscriptionCheckMiddleware'
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
            BASE_DIR / 'templates' , #here is for load all the views of the apps that exist in the ERP

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

#----------------------------configuration of celery---------------------------------
if TYPE_VERSION=='CLOUD':
    #to run the worker of celery use the next command in the terminal only if you have the version cloud

    #celery -A core worker -l info
    CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://127.0.0.1:6379/0')
    CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND', "redis://127.0.0.1:6379/0")
    CELERY_WORKER_PREFETCH_MULTIPLIER=1
    
    CELERY_ACCEPT_CONTENT = ['json']
    CELERY_TASK_SERIALIZER = 'json'
    CELERY_RESULT_SERIALIZER = 'json'

    from celery.schedules import crontab

    #here we will configure the tasks that will be run in background with celery
    #here after we will to read all the task that exist in all the apps for if one have event that would like meminder
    CELERY_BEAT_SCHEDULE = {
        # Task 1: send reminders to the customers of the appoints of the user (this run 24/7)
        "enviar-recordatorios-cada-5-min": {
            "task": "apps.agenda.tasks.send_reminders",
            "schedule": 300,  # this is run by 5 minutes
        },

        
        # Task 2: Monthly Renewal for can send more message of whatsapp (run only the day 1 of the month to 1:00 AM)
            "renovar-limites-mensuales": {
                "task": "apps.agenda.tasks.renovar_limites_mensuales", 
                "schedule": crontab(day_of_month=1, hour=1, minute=0),
            },
    }


#----------------------------configuration of django Q for task in background---------------------------------
'''

INSTALLED_APPS = [
    'django_q'
]


Q_CLUSTER = {
    'name': 'erp_cluster',        # Name of the task cluster
    'workers': 4,                 # Number of workers (processes) that run tasks in parallel
    'timeout': 60,                # Maximum time in seconds a task is allowed before being marked as failed
    'retry': 120,                 # Time in seconds to retry a failed task
    'queue_limit': 50,            # Maximum number of tasks allowed in the queue
    'bulk': 10,                   # Number of tasks processed per cycle (for performance)
    'orm': 'default',             # Use Django's database as the backend (instead of Redis, etc.)
}
'''

#---------------------HERE WE WILL GET THE KEYS OF FACEBOOKS IF EXIST IN THE ENV-----------------------
FB_APP_ID=os.getenv('FB_APP_ID', '')
FB_APP_SECRET=os.getenv('FB_APP_SECRET', '')




#Here we will to connect with the database of the system
if(TYPE_VERSION=='CLOUD'):
    #This allows you to connect to your cloud database, such as PostgreSQL, MySQL, etc.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.getenv('DB_NAME', 'default_db_name'),
            'USER': os.getenv('DB_USER', 'default_user'),
            'PASSWORD': os.getenv('DB_PASS', 'default_password'),
            'HOST': os.getenv('DB_HOST', 'localhost'),
            'PORT': os.getenv('DB_PORT', '5432')
        }
    }
else:
    #when the software is intall in a desktop, we will use sqlite 
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'plus.sqlite3',  # file SQLite local
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
USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = 'UTC'  # save all the information of type date like UTC in the database

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
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
    BASE_DIR / 'apps',
]

#setting login
AUTH_USER_MODEL = 'core.CustomUser' #this is the model that need the login of the user
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/'

AUTHENTICATION_BACKENDS = [
'core.backends.EmailHashBackend'
]


#------------------------------EMAILS---------------------------------------------------
# Email backend (SMTP real)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'yourservices@example.com') # email that be show like remitent

# setting of the server SMTP
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')        # server SMTP
EMAIL_PORT = 587                     # port SMTP (587 = STARTTLS, 465 = SSL)
EMAIL_USE_TLS = True                 # use TLS
EMAIL_USE_SSL = False                # only if the port is 465
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', 'youremail@gmail.com')   # your user of email
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', 'your_password')        # your password or app password


#----------------------------configuration of allowed hosts---------------------------------
#this is for added the variable of the path 
from decouple import config
ALLOWED_HOSTS = config("DJANGO_ALLOWED_HOSTS", default="127.0.0.1,localhost").split(",")

#----------------------------files upload for the user (for example PDFs, images, etc)-------------------------------------
#first we will see if the user have the version of desktop or the version cloud 
if(TYPE_VERSION=='CLOUD'):
    #if the version is type cloud, we will get the path of our server for save the file
    MEDIA_URL = os.getenv('PATH_CLOUD_URL', '/media/')
    MEDIA_ROOT = os.getenv('PATH_CLOUD_ROOT', BASE_DIR / 'media')
else:
    #if the version is of desktop, we will to save the file in the drive of the user
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media' 
