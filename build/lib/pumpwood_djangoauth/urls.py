"""Consolidate all base Pumpwood urls."""
from django.urls import include
from django.urls import re_path as url


urlpatterns = [
    # Registration end-points
    url(r'', include('pumpwood_djangoauth.registration.urls')),
    url(r'', include('pumpwood_djangoauth.system.urls')),
    url(r'', include('pumpwood_djangoauth.metabase.urls')),
    url(r'', include('pumpwood_djangoauth.i8n.urls')),
    url(r'', include('pumpwood_djangoauth.api_permission.urls')),
    url(r'', include('pumpwood_djangoauth.row_permission.urls')),
    url(r'', include('pumpwood_djangoauth.groups.urls')),
    url(r'', include('pumpwood_djangoauth.service_views.urls')),
]
