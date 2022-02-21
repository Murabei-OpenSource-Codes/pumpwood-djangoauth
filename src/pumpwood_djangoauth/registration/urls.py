from pumpwood_djangoviews.routers import PumpWoodRouter
from django.conf.urls import url
from pumpwood_djangoauth.registration import views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestUser)

urlpatterns = [
    url(r'^registration/login/$', views.login_view,
        name='rest__registration__login'),
    url(r'^registration/logout/$', views.logout_view,
        name='rest__registration__logout'),
    url(r'^registration/check/$', views.check_logged,
        name='rest__registration__checklogged'),
    url(r'^registration/retrieveauthenticateduser/$',
        views.retrieve_authenticated_user,
        name='rest__registration__retrieveauthenticateduser'),
]

urlpatterns += pumpwoodrouter.urls
