import os
from django.utils.translation import ugettext_lazy as _

######################
# MEZZANINE SETTINGS #
######################

# The following settings are already defined with default values in
# the ``defaults.py`` module within each of Mezzanine's apps, but are
# common enough to be put here, commented out, for conveniently
# overriding. Please consult the settings documentation for a full list
# of settings Mezzanine implements:
# http://mezzanine.jupo.org/docs/configuration.html#default-settings

# Controls the ordering and grouping of the admin menu.

ADMIN_MENU_ORDER = (
    ('Content', ('pages.Page', 'blog.BlogPost',
                 'generic.ThreadedComment', (_('Media Library'), 'fb_browse'),)),
    (_('SSC_Configs'), ('ssc_configs.GroupInfo',)),
    ('Site', ('sites.Site', 'redirects.Redirect', 'conf.Setting')),
    ('Users', ('auth.User', 'auth.Group',)),

)

# A three item sequence, each containing a sequence of template tags
# used to render the admin dashboard.
#
# DASHBOARD_TAGS = (
#     ('blog_tags.quick_blog', 'mezzanine_tags.app_list'),
#     ('comment_tags.recent_comments',),
#     ('mezzanine_tags.recent_actions',),
# )

# A sequence of templates used by the ``page_menu`` template tag. Each
# item in the sequence is a three item sequence, containing a unique ID
# for the template, a label for the template, and the template path.
# These templates are then available for selection when editing which
# menus a page should appear in. Note that if a menu template is used
# that doesn't appear in this setting, all pages will appear in it.

PAGE_MENU_TEMPLATES = (
    (1, _('Top navigation bar'), 'pages/menus/dropdown.html'),
    (2, _('Left-hand tree'), 'pages/menus/tree.html'),
    #     (3, _('Footer'), 'pages/menus/footer.html'),
)

# A sequence of fields that will be injected into Mezzanine's (or any
# library's) models. Each item in the sequence is a four item sequence.
# The first two items are the dotted path to the model and its field
# name to be added, and the dotted path to the field class to use for
# the field. The third and fourth items are a sequence of positional
# args and a dictionary of keyword args, to use when creating the
# field instance. When specifying the field class, the path
# ``django.models.db.`` can be omitted for regular Django model fields.

EXTRA_MODEL_FIELDS = (
    # Relating blog posts to site pages in order to announce theme
    (
        # Dotted path to field.
        'mezzanine.blog.models.BlogPost.page',
        # Dotted path to field class.
        'ForeignKey',
        # Positional args for field class.
        ('pages.Page',),
        # Keyword args for field class.
        {'blank': True, 'null': True, 'verbose_name': _('Related Page')},
    ),
    # Allow user to change read more text for blog posts
    (
        # Dotted path to field.
        'mezzanine.blog.models.BlogPost.read_more_text',
        # Dotted path to field class.
        'django.db.models.CharField',
        # Positional args for field class.
        (_('Read More Text'),),
        # Keyword args for field class.
        {'blank': True, 'null': True, 'max_length': 500},
    ),
    # Add an awesome image to be used as a parallax for galleries
    (
        # Dotted path to field.
        'mezzanine.galleries.models.Gallery.parallax_image',
        # Dotted path to field class.
        'mezzanine.core.fields.FileField',
        # Positional args for field class.
        (_('Parallax Image'),),
        # Keyword args for field class.
        {'blank': True, 'null': True, 'upload_to': 'galleries/parallaxes', 'format': 'Image',
         'max_length': 500},
    ),
)

# Setting to turn on featured images for blog posts. Defaults to False.

BLOG_USE_FEATURED_IMAGE = True

BLOG_SLUG = 'announcements'

# ReCaptcha settings
RECAPTCHA_PUBLIC_KEY = '6LeQbTMUAAAAANtR7JIMvi6UpUiHdCvXYAwJt1WD'
NOCAPTCHA = True
COMMENT_FORM_CLASS = 'mezzacaptcha.forms.CaptchaThreadedCommentForm'

# If True, the django-modeltranslation will be added to the
# INSTALLED_APPS setting.
USE_MODELTRANSLATION = True

# Use HTML5 special inputs

FORMS_USE_HTML5 = True

########################
# MAIN DJANGO SETTINGS #
########################

# Hosts/domain names that are valid for this site; required if DEBUG is False
# See https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = [
    'ssc.ce.sharif.edu',
    'localhost:8000',
    'localhost',
]

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Asia/Tehran'

# If you set this to True, Django will use timezone-aware datetimes.
USE_TZ = True

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fa-IR'

# Supported languages
LANGUAGES = (
    ('fa', _('Persian')),
    ('en', _('English')),
)

# A boolean that turns on/off debug mode. When set to ``True``, stack traces
# are displayed for error pages. Should always be set to ``False`` in
# production. Best set to ``True`` in local_settings.py
DEBUG = False

# Whether a user's session cookie expires when the Web browser is closed.
SESSION_EXPIRE_AT_BROWSER_CLOSE = False

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = True

# The numeric mode to set newly-uploaded files to. The value should be
# a mode you'd pass directly to os.chmod.
FILE_UPLOAD_PERMISSIONS = 0o644

#############
# DATABASES #
#############

DATABASES = {
    'default': {
        # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'ENGINE': 'django.db.backends.',
        # DB name or path to database file if using sqlite3.
        'NAME': '',
        # Not used with sqlite3.
        'USER': '',
        # Not used with sqlite3.
        'PASSWORD': '',
        # Set to empty string for localhost. Not used with sqlite3.
        'HOST': '',
        # Set to empty string for default. Not used with sqlite3.
        'PORT': '',
    }
}

#########
# PATHS #
#########

# Full filesystem path to the project.
PROJECT_APP_PATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_APP = os.path.basename(PROJECT_APP_PATH)
PROJECT_ROOT = BASE_DIR = os.path.dirname(PROJECT_APP_PATH)

# Every cache key will get prefixed with this value - here we set it to
# the name of the directory the project is in to try and use something
# project specific.
CACHE_MIDDLEWARE_KEY_PREFIX = PROJECT_APP

# URL prefix for static files.
# Example: 'http://media.lawrence.com/static/'
STATIC_URL = '/static/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' 'static/' subdirectories and in STATICFILES_DIRS.
# Example: '/home/media/media.lawrence.com/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, STATIC_URL.strip('/'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: 'http://media.lawrence.com/media/', 'http://example.com/media/'
MEDIA_URL = '/media/'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: '/home/media/media.lawrence.com/media/'
MEDIA_ROOT = os.path.join(PROJECT_ROOT, *MEDIA_URL.strip('/').split('/'))

# Package/module name to import the root urlpatterns from for the project.
ROOT_URLCONF = '%s.urls' % PROJECT_APP

# Put strings here, like '/home/html/django_templates'
# or 'C:/www/django/templates'.
# Always use forward slashes, even on Windows.
# Don't forget to use absolute paths, not relative paths.
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(PROJECT_ROOT, 'templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.tz',
                'mezzanine.conf.context_processors.settings',
                'mezzanine.pages.context_processors.page',
            ],
            'builtins': [
                'mezzanine.template.loader_tags'
            ]
        },
    },
]

LOCALE_PATHS = (os.path.join(PROJECT_ROOT, 'locale'),)

################
# APPLICATIONS #
################

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.sitemaps',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'djcelery_email',
    'ssc_template',
    'captcha',
    'mezzacaptcha',
    'mezzanine.boot',
    'mezzanine.conf',
    'mezzanine.core',
    'mezzanine.generic',
    'mezzanine.pages',
    'mezzanine.blog',
    'mezzanine.forms',
    'mezzanine.galleries',
    'tempita',
    'ssc_configs',
    'transactions',
    'media_manager',
    'screens',
    # 'mezzanine.twitter',
    # 'mezzanine.accounts',
    # 'mezzanine.mobile',
    'shortener',
    'certificates',
    'subprocess_manager',
    'dbbackup',
)

DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/var/backups'}

# List of middleware classes to use. Order is important; in the request phase,
# these middleware classes will be applied in the order given, and in the
# response phase the middleware will be applied in reverse order.
MIDDLEWARE_CLASSES = (
    'ssc_configs.ForceDefaultLanguageMiddleware',

    'mezzanine.core.middleware.UpdateCacheMiddleware',

    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'mezzanine.core.request.CurrentRequestMiddleware',
    'mezzanine.core.middleware.RedirectFallbackMiddleware',
    'mezzanine.core.middleware.TemplateForDeviceMiddleware',
    'mezzanine.core.middleware.TemplateForHostMiddleware',
    'mezzanine.core.middleware.AdminLoginInterfaceSelectorMiddleware',
    'mezzanine.core.middleware.SitePermissionMiddleware',
    # Uncomment the following if using any of the SSL settings:
    # 'mezzanine.core.middleware.SSLRedirectMiddleware',
    'mezzanine.pages.middleware.PageMiddleware',
    'mezzanine.core.middleware.FetchFromCacheMiddleware',
)

# Store these package names here as they may change in the future since
# at the moment we are using custom forks of them.
PACKAGE_NAME_FILEBROWSER = 'filebrowser_safe'
PACKAGE_NAME_GRAPPELLI = 'grappelli_safe'

#########################
# OPTIONAL APPLICATIONS #
#########################

# These will be added to ``INSTALLED_APPS``, only if available.
OPTIONAL_APPS = (
    'debug_toolbar',
    'django_extensions',
    'compressor',
    PACKAGE_NAME_FILEBROWSER,
    PACKAGE_NAME_GRAPPELLI,
)

#########################
# FILE BROWSER SETTINGS #
#########################

# Commented to prevent a bug!
# FILEBROWSER_EXTENSIONS = {
#     'Image': ['.jpg', '.jpeg', '.gif', '.png', '.tif', '.tiff'],
#     'Document': ['.pdf', '.doc', '.rtf', '.txt', '.xls', '.csv'],
#     'Video': ['.mov', '.wmv', '.mpeg', '.mpg', '.avi', '.rm'],
#     'Audio': ['.mp3', '.mp4', '.wav', '.aiff', '.midi', '.m4p'],
#     'Compressed': ['.zip'],
# }
#
# FILEBROWSER_SELECT_FORMATS = {
#     'file': ['Image', 'Document', 'Video', 'Audio', 'Compressed'],
#     'image': ['Image'],
#     'document': ['Document'],
#     'media': ['Video', 'Audio'],
#     'compressed': ['Compressed'],
# }



##########
# CELERY #
##########

BROKER_URL = 'redis://localhost:6379/1'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
EMAIL_BACKEND = 'djcelery_email.backends.CeleryEmailBackend'
CELERY_EMAIL_TASK_CONFIG = {
    'max_retries': 8,
    'queue': 'mail_queue',
}

#######################
# LDAP AUTHENTICATION #
#######################

import ldap
from django_auth_ldap.config import LDAPSearch, PosixGroupType

# Baseline configuration.
AUTH_LDAP_SERVER_URI = 'ldap://localhost'

LDAP_SEARCH_DOMAIN = 'dc=ssc,dc=ce,dc=sharif,dc=edu'

AUTH_LDAP_BIND_DN = 'cn=admin,' + LDAP_SEARCH_DOMAIN
AUTH_LDAP_BIND_PASSWORD = 'pass'
AUTH_LDAP_USER_SEARCH = LDAPSearch('ou=users,' + LDAP_SEARCH_DOMAIN,
                                   ldap.SCOPE_SUBTREE, '(uid=%(user)s)')
# or perhaps:
# AUTH_LDAP_USER_DN_TEMPLATE = 'uid=%(user)s,ou=users,dc=example,dc=com'

# Set up the basic group parameters.
AUTH_LDAP_GROUP_SEARCH = LDAPSearch('ou=groups,' + LDAP_SEARCH_DOMAIN,
                                    ldap.SCOPE_SUBTREE, '(objectClass=groupOfNames)'
                                    )
AUTH_LDAP_GROUP_TYPE = PosixGroupType()

# Simple group restrictions
# AUTH_LDAP_REQUIRE_GROUP = 'cn=enabled,ou=groups,dc=amira,dc=li'
# AUTH_LDAP_DENY_GROUP = 'cn=disabled,ou=groups,dc=amira,dc=li'

# Populate the Django user from the LDAP directory.
AUTH_LDAP_USER_ATTR_MAP = {
    'first_name': 'givenName',
    'last_name': 'sn',
    'email': 'mail'
}

AUTH_LDAP_PROFILE_ATTR_MAP = {
    'employee_number': 'employeeNumber'
}

AUTH_LDAP_USER_FLAGS_BY_GROUP = {
    'is_active': 'cn=active,ou=groups,' + LDAP_SEARCH_DOMAIN,
    'is_staff': 'cn=staff,ou=groups,' + LDAP_SEARCH_DOMAIN,
    'is_superuser': 'cn=superuser,ou=groups,' + LDAP_SEARCH_DOMAIN,
}

# AUTH_LDAP_PROFILE_FLAGS_BY_GROUP = {
#     'is_awesome': 'cn=awesome,ou=django,ou=groups,dc=amira,dc=li',
# }

# This is the default, but I like to be explicit.
AUTH_LDAP_ALWAYS_UPDATE_USER = True

# Use LDAP group membership to calculate group permissions.
AUTH_LDAP_FIND_GROUP_PERMS = True

# Cache group memberships for an hour to minimize LDAP traffic
AUTH_LDAP_CACHE_GROUPS = True
AUTH_LDAP_GROUP_CACHE_TIMEOUT = 3600

# Keep ModelBackend around for per-user permissions and maybe a local
# superuser.
AUTHENTICATION_BACKENDS = (
    'django_auth_ldap.backend.LDAPBackend',
    'django.contrib.auth.backends.ModelBackend',
)

##########################
# URL Shortener Settings #
##########################

import string

SHORTENER_SLUG_CHARSET = string.ascii_lowercase + string.digits
SHORTENER_SLUG_LENGTH = 8

########################
# Certificate Settings #
########################

XELATEX_PATH = '/usr/bin/xelatex'

##################
# LOCAL SETTINGS #
##################

# Allow any settings to be defined in local_settings.py which should be
# ignored in your version control system allowing for settings to be
# defined per machine.

# Instead of doing 'from .local_settings import *', we use exec so that
# local_settings has full access to everything defined in this module.

f = os.path.join(PROJECT_APP_PATH, 'local_settings.py')
if os.path.exists(f):
    exec(open(f, 'rb').read())

####################
# DYNAMIC SETTINGS #
####################

# set_dynamic_settings() will rewrite globals based on what has been
# defined so far, in order to provide some better defaults where
# applicable. We also allow this settings module to be imported
# without Mezzanine installed, as the case may be when using the
# fabfile, where setting the dynamic settings below isn't strictly
# required.
try:
    from mezzanine.utils.conf import set_dynamic_settings
except ImportError:
    pass
else:
    set_dynamic_settings(globals())
