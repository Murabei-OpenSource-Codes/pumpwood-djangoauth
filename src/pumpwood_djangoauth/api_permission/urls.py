from pumpwood_djangoviews.routers import PumpWoodRouter
from django.conf.urls import url
from pumpwood_djangoauth.api_permission import views
from knox import views as knox_views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicy)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicyAction)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionGroup)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionUserGroupM2M)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicyGroupM2M)
pumpwoodrouter.register(viewset=views.RestPumpwoodPermissionPolicyUserM2M)

urlpatterns = [
]

urlpatterns += pumpwoodrouter.urls
