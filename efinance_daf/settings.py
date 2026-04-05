"""
Django settings for efinance_daf project.
"""

import os
from pathlib import Path
from decouple import config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me-in-production-!@#$%^&*()')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=True, cast=bool)

from decouple import config

# Domain settings
DOMAIN_NAME = config('DOMAIN_NAME', default='e-fintrack-dgrad.com')
SITE_URL = config('SITE_URL', default=f'https://{DOMAIN_NAME}')

ALLOWED_HOSTS = [host.strip() for host in config('ALLOWED_HOSTS', default='localhost,127.0.0.1,testserver').split(',')]
ALLOWED_HOSTS.append(DOMAIN_NAME)

# Ajoute manuellement le host avec port si tu utilises runserver
if '187.77.171.80:8000' not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append('187.77.171.80')

print("ALLOWED_HOSTS =", ALLOWED_HOSTS)

# Force HTTP en développement
SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',  # Pour le formatage des nombres
    
    # Third-party apps
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_extensions',
    
    # Local apps
    'accounts',
    'banques',
    'demandes',
    'recettes',
    'releves',
    'rapports',
    'etats',
    'tableau_bord_feuilles',
    'clotures',
    'rbac',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'efinance_daf.middleware.SessionInterruptedMiddleware',  # Gestion gracieuse des sessions interrompues (juste après SessionMiddleware)
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'accounts.auto_permissions_middleware.AutoPermissionsMiddleware',  # Auto-permissions pour les rôles
    'accounts.middleware.AdminAccessMiddleware',  # Gestion des accès selon les rôles
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'efinance_daf.urls'



TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = 'efinance_daf.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

# Configuration de la base de données
# SQLite par défaut | Pour PostgreSQL : USE_POSTGRESQL=True dans .env
USE_POSTGRESQL = config('USE_POSTGRESQL', default=False, cast=bool)

if USE_POSTGRESQL:
    # Connexion PostgreSQL
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': config('DB_NAME', default='FINTRACK'),
            'USER': config('DB_USER', default='postgres'),
            'PASSWORD': config('DB_PASSWORD', default='123456'),
            'HOST': config('DB_HOST', default='localhost'),
            'PORT': config('DB_PORT', default='5432'),
        }
    }
else:
    # SQLite pour le développement/test
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/5.0/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.0/ref/settings/#i18n

LANGUAGE_CODE = 'fr-fr'

TIME_ZONE = 'Africa/Kinshasa'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = config('STATIC_URL', default='/static/')
STATIC_ROOT = config('STATIC_ROOT', default=BASE_DIR / 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = config('MEDIA_URL', default='/media/')
MEDIA_ROOT = config('MEDIA_ROOT', default=BASE_DIR / 'media')

# Production settings
if not DEBUG:
    # Security settings
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = 'DENY'
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    
    # Session security - MODIFIÉ pour multi-machines
    SESSION_COOKIE_SECURE = False  # False pour HTTP
    CSRF_COOKIE_SECURE = False     # False pour HTTP
    SECURE_SSL_REDIRECT = False    # False pour HTTP
    
    # CSRF settings for multiple domains/machines
    CSRF_TRUSTED_ORIGINS = [
        "http://187.77.171.80:8000",
        "http://187.77.171.80",
        "https://187.77.171.80",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Session settings for multiple domains
    SESSION_COOKIE_DOMAIN = None  # Permet le partage entre sous-domaines
    SESSION_COOKIE_AGE = 86400 * 7  # 7 jours
    SESSION_SAVE_EVERY_REQUEST = True
    
    # CORS settings pour multi-machines
    CORS_ALLOWED_ORIGINS = [
        "http://187.77.171.80:8000",
        "http://187.77.171.80",
        "https://187.77.171.80",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
else:
    # Settings pour DEBUG=True
    CSRF_TRUSTED_ORIGINS = [
        "http://187.77.171.80:8000",
        "http://187.77.171.80",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    SESSION_COOKIE_SECURE = False
    CSRF_COOKIE_SECURE = False
    SESSION_COOKIE_DOMAIN = None

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom User Model
AUTH_USER_MODEL = 'accounts.User'

# Django Admin Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
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

# Admin template customization
ADMIN_SITE_TITLE = "e-FinTrack Administration"
ADMIN_SITE_HEADER = "e-FinTrack Administration"
ADMIN_INDEX_TITLE = "Bienvenue dans l'administration e-FinTrack"

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Login URLs
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = '/'  # Redirection vers la racine (dashboard)
LOGOUT_REDIRECT_URL = 'accounts:login'

# File upload settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

# Session settings
SESSION_COOKIE_AGE = 3600  # 1 hour (en secondes)
SESSION_SAVE_EVERY_REQUEST = True
SESSION_COOKIE_SECURE = False  # True en production avec HTTPS
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_EXPIRE_AT_BROWSER_CLOSE = False  # La session persiste après fermeture du navigateur

# Email settings (configure for production)
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'efinance.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': True,
        },
        'etats': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
CSRF_TRUSTED_ORIGINS = ['http://187.77.171.80:8000']
