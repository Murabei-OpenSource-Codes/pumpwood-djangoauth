"""URLs for system end-points."""
from urllib.parse import urljoin
from django.urls import path
from pumpwood_djangoviews.routers import PumpWoodRouter
from pumpwood_djangoauth.system import views
from pumpwood_djangoauth.config import storage_object, MEDIA_URL


pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestKongService)
pumpwoodrouter.register(viewset=views.RestKongRoute)


# Create an serve media object to serve static files from storage
servemedia_object = views.ServeMediaFiles(storage_object=storage_object)

urlpatterns = [
    path(
        'rest/pumpwood/routes/', views.view__get_kong_routes,
        name='rest__pumpwood_routes'),
    path(
        'rest/pumpwood/endpoints/', views.view__get_registred_endpoints,
        name='rest__pumpwood_endpoits'),
    path(
        'rest/pumpwood/dummy-call/', views.view__dummy_call,
        name='rest__dummy_call'),
    path(
        'rest/pumpwood/dummy-raise/', views.view__dummy_raise,
        name='rest__dummy_raise'),

    # Retrieve Media Files
    path(urljoin(MEDIA_URL, '<path:file_path>'),
         servemedia_object.as_view(),
         name="media__endpoint")
]

urlpatterns += pumpwoodrouter.urls
