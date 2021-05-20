import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = os.environ['DEBUG'] == 'True' # environment vars are strings. "convert" to boolean. lol, Python
SECRET_KEY = os.environ['SECRET_KEY'] == 'y+0!wv4jya+0t_u9zfkr1k746w((tf17%mi#c-$y^gdr=z7pf7' 

ALLOWED_HOSTS = [
  # TODO: add your Google Cloud Project-ID here
    'geelong-disc.ts.r.appspot.com',
    'localhost',
    '127.0.0.1', # for local testing 
]

# TODO: add your project apps here
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'prediction',
    'import_export',
    'widget_tweaks'
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

# TODO: update root project directory for urlconf and wsgi app
ROOT_URLCONF = 'Property_Portal.urls' # ROOT-PROJECT-DIRECTORY is the directory where this settings.py file is
WSGI_APPLICATION = 'wsgi.application'

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

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases
DATABASES = {
    'default': {
      'ENGINE': 'django.db.backends.postgresql',
      'HOST': os.environ['DB_HOST'],
      'PORT': os.environ['DB_PORT'],
      'NAME': os.environ['DB_NAME'],
      'USER': os.environ['DB_USER'],
      'PASSWORD': os.environ['DB_PASSWORD']
    }
}

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

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True
'''
# Static files (CSS, JavaScript, Images)
STATIC_URL = os.environ['STATIC_URL'] # /static/ if DEBUG else Google Cloud bucket url

# collectstatic directory (located OUTSIDE the base directory)
# TODO: configure the name and path to your static bucket directory (where collectstatic will copy to)
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR), 'geelong-disc-static')

STATICFILES_DIRS = [
  # TODO: configure the name and path to your development static directory
    os.path.join(BASE_DIR, 'static'), # static directory (in the top level directory) for local testing
]'''