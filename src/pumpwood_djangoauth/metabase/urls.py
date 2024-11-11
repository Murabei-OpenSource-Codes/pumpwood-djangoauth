"""Django URLs."""
from pumpwood_djangoauth.metabase import views
from pumpwood_djangoviews.routers import PumpWoodRouter


pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestMetabaseDashboard)
pumpwoodrouter.register(viewset=views.RestMetabaseDashboardParameter)

urlpatterns = [
]

urlpatterns += pumpwoodrouter.urls
