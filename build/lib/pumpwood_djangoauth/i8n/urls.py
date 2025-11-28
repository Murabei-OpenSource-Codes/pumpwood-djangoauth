"""Register URL."""
from pumpwood_djangoviews.routers import PumpWoodRouter
from pumpwood_djangoauth.i8n import views


pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestPumpwoodI8nTranslation)

urlpatterns = [
]

urlpatterns += pumpwoodrouter.urls
