"""Create URLs for api_permission models."""
from pumpwood_djangoviews.routers import PumpWoodRouter
from pumpwood_djangoauth.groups import views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestPumpwoodUserGroup)
pumpwoodrouter.register(viewset=views.RestPumpwoodUserGroupM2M)

urlpatterns = [
]

urlpatterns += pumpwoodrouter.urls
