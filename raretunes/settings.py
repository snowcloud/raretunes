# Django settings for raretunes project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'raretunesdb',                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'
DATE_FORMAT='%d %B %Y, %H:%M'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
# MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
# MEDIA_URL = ''

import os
import sys
PROJECT_PATH = os.path.abspath(os.path.split(__file__)[0])

sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))
sys.path.insert(0, os.path.join(PROJECT_PATH, "libs"))
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'static')
TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, 'sitetemplates')
)

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin/media/'

# Make this unique, put your own key here or override in settings_local.py
SECRET_KEY = 'ju7vWreJndmIshuN5mmFjTYgeRFHCyuMpWwYXOrzJrVwwXvx'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = ( 
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request"
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    "pagination.middleware.PaginationMiddleware",
    "django.contrib.redirects.middleware.RedirectFallbackMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
)

ROOT_URLCONF = 'raretunes.urls'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.flatpages',
    'django.contrib.humanize',
    'django.contrib.markup',
    'django.contrib.redirects',
    'contact_form',
    'pagination',
    'tagging',
    'home',
    'recordings',
    'scutils'
    
)
#  used in recordings.templatetags.recordingtags
LICENCE_PUBLIC_DOMAIN = '<p>This recording is Public Domain.</p>'
LICENCE_CC_BY_NC_SA_2_5_SCOTLAND = '<!--Creative Commons License--><a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/"><img alt="Creative Commons License" style="border-width: 0" src="http://i.creativecommons.org/l/by-nc-sa/2.5/scotland/88x31.png"/></a><br/>These recordings are licensed under a <a rel="license" href="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/">Creative Commons Attribution-Noncommercial-Share Alike 2.5 UK: Scotland License</a>.<!--/Creative Commons License--><!-- <rdf:RDF xmlns="http://web.resource.org/cc/" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"><Work rdf:about=""><license rdf:resource="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/" /><dc:type rdf:resource="http://purl.org/dc/dcmitype/Sound" /></Work><License rdf:about="http://creativecommons.org/licenses/by-nc-sa/2.5/scotland/"><permits rdf:resource="http://web.resource.org/cc/Reproduction"/><permits rdf:resource="http://web.resource.org/cc/Distribution"/><requires rdf:resource="http://web.resource.org/cc/Notice"/><requires rdf:resource="http://web.resource.org/cc/Attribution"/><prohibits rdf:resource="http://web.resource.org/cc/CommercialUse"/><permits rdf:resource="http://web.resource.org/cc/DerivativeWorks"/><requires rdf:resource="http://web.resource.org/cc/ShareAlike"/></License></rdf:RDF> -->'
LICENCE_CC_BY_SA_3_0 = '<a target="_blank" href="http://creativecommons.org/licenses/by-sa/3.0/" rel="license"><img src="http://i.creativecommons.org/l/by-sa/3.0/88x31.png" alt="Attribution-Share Alike 3.0" style="border: medium none ;"/></a>'
LICENCE_NOT_DEFINED = '<p>Licence not defined.</p>'
LICENCES = { 
    'by-nc-sa_2.5_scotland': LICENCE_CC_BY_NC_SA_2_5_SCOTLAND, 
    'by-sa_3.0': LICENCE_CC_BY_SA_3_0, 
    'public_domain': LICENCE_PUBLIC_DOMAIN
    }
# used in recordings.models
LICENCE_TYPES = (
            ('by_2.5_scotland', 'Creative Commons, Attribution 2.5 UK: Scotland'),
            ('by-nc_2.5_scotland', 'Creative Commons, Attribution-Noncommercial 2.5 UK: Scotland'),
            ('by-nc-nd_2.5_scotland', 'Creative Commons, Attribution-Noncommercial-No Derivative Works 2.5 UK: Scotland'),
            ('by-nc-sa_2.5_scotland', 'Creative Commons, Attribution-Noncommercial-Share Alike 2.5 UK: Scotland'),
            ('by-nd_2.5_scotland', 'Creative Commons, Attribution-No Derivative Works 2.5 UK: Scotland'),
            ('by-sa_2.5_scotland', 'Creative Commons, Attribution-Share Alike 2.5 UK: Scotland'),
            ('by-sa_3.0', 'Creative Commons, Attribution-Share Alike 3.0'),
            ('public_domain', 'public domain'),
        )
LICENCE_TYPES_DEFAULT = 'by-nc-sa_2.5_scotland'



# override any of the above in your own settings_local.py
try:
    from settings_local import *
except ImportError:
    pass

