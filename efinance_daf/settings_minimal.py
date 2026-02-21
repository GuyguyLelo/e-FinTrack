# Configuration minimale pour contourner les problèmes de middlewares
DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1']

BASE_DIR = Path(__file__).resolve().parent.parent

# Applications essentielles (excluant celles qui causent des problèmes)
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'accounts',
    'banques',
    'demandes',
    'recettes',
    'tableau_bord_feuilles',
    'rest_framework',
]
