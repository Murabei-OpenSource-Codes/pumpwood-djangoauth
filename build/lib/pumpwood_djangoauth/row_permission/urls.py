"""Row permission views."""
from pumpwood_djangoviews.routers import PumpWoodRouter
from pumpwood_djangoauth.row_permission import views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(views.RestPumpwoodRowPermission)
pumpwoodrouter.register(views.RestPumpwoodRowPermissionGroupM2M)
pumpwoodrouter.register(views.RestPumpwoodRowPermissionUserM2M)

urlpatterns = [
]

urlpatterns += pumpwoodrouter.urls
