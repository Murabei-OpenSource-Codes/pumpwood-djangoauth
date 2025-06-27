"""Create URLs for api_permission models."""
from django.urls import path
from pumpwood_djangoviews.routers import PumpWoodRouter
from pumpwood_djangoauth.api_permission import views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicy)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicyAction)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicyGroupM2M)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicyUserM2M)

urlpatterns = [
    path(
        'rest/api-permission/has-self-permission/',
        views.view__has_permission,
        name='rest__api_permission__has_permission'),
]

urlpatterns += pumpwoodrouter.urls
