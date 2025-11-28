"""URLs for service end-points."""
from django.urls import path
from pumpwood_djangoauth.service_views import views


urlpatterns = [
    path(
        'service/pumpwood-auth-app/health-check/',
        views.view__health_check,
        name='service__health_check'),
    path(
        'service/pumpwood-auth-app/clear-diskcache/',
        views.view__clear_diskcache,
        name='service__clear_diskcache'),

    # Legacy health_check end-point
    path(
        'health-check/pumpwood-auth-app/', views.view__health_check,
        name='service__health_check_legacy'),
]
