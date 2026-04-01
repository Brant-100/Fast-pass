"""URL configuration for endor_park project."""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

_static = settings.STATIC_URL.rstrip('/')
_favicon_url = f'{_static}/favicon.svg' if _static.startswith('/') else f'/{_static}/favicon.svg'

urlpatterns = [
    path('admin/', admin.site.urls),
    # Browsers request /favicon.ico before HTML; redirect to static SVG.
    path(
        'favicon.ico',
        RedirectView.as_view(url=_favicon_url, permanent=False),
    ),
    path('', include('fastpass.urls')),
]
