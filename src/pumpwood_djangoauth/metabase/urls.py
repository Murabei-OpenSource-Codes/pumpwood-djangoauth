from urllib.parse import urljoin
from django.urls import path
from django.conf.urls import url
from pumpwood_djangoviews.routers import PumpWoodRouter
from pumpwood_djangoauth.config import storage_object, MEDIA_URL
from pumpwood_djangoauth.metabase import views


pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestMetabaseDashboard)
pumpwoodrouter.register(viewset=views.RestMetabaseDashboardParameter)

urlpatterns = [
]

urlpatterns += pumpwoodrouter.urls
