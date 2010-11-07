import os
from settings_local import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/home/adeleinr/Development/django-projects/webme/db.cnf',
        },
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'media_rsc')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://localhost/webme/media_rsc/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

TEMPLATE_CONTEXT_PROCESSORS =  (
  'django.core.context_processors.request',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

# Default: ('django.contrib.auth.backends.ModelBackend',)
# A tuple of authentication backend classes (as strings)
# to use when attempting to authenticate a use
AUTHENTICATION_BACKENDS = (
   'socialregistration.auth.FacebookAuth', 
   'django.contrib.auth.backends.ModelBackend',                                            
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'socialregistration.middleware.FacebookMiddleware',

)

ROOT_URLCONF = 'webme.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
   os.path.join(PROJECT_DIR, 'Templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'colorific',
    'django_extensions',
    'debug_toolbar',
    'socialregistration',
    'taggit'
)


INTERNAL_IPS = ('127.0.0.1',)
AUTH_PROFILE_MODULE = "colorific.UserProfile"
LOGIN_URL = "/colorific/login_user"
LOGIN_REDIRECT_URL = "/colorific"

DEBUG_TOOLBAR_CONFIG = {
   'INTERCEPT_REDIRECTS': False,
}





