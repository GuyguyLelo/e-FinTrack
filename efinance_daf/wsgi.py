"""
WSGI config for efinance_daf project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'efinance_daf.settings')

application = get_wsgi_application()

