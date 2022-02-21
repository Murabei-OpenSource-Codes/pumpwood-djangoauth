from pumpwood_djangoviews.routers import PumpWoodRouter
from django.conf.urls import url
from pumpwood_djangoauth.system import views


pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestKongService)
pumpwoodrouter.register(viewset=views.RestKongRoute)


urlpatterns = [
    url(r'^pumpwood/routes/$', views.view__get_kong_routes,
        name='rest__pumpwood_routes'),
    url(r'^pumpwood/endpoints/$', views.view__get_registred_endpoints,
        name='rest__pumpwood_endpoits'),
    url(r'^pumpwood/dummy-call/$', views.view__dummy_call,
        name='rest__dummy_call'),
]

urlpatterns += pumpwoodrouter.urls
