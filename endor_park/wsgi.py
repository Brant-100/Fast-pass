"""
WSGI config for endor_park project.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'endor_park.settings')

application = get_wsgi_application()
