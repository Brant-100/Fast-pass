"""
ASGI config for endor_park project.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'endor_park.settings')

application = get_asgi_application()
