from pumpwood_djangoviews.routers import PumpWoodRouter
from django.conf.urls import url
from pumpwood_djangoauth.registration import views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestUser)

urlpatterns = [
    url(r'^rest/registration/login/$', views.login_view,
        name='rest__registration__login'),
    url(r'^rest/registration/logout/$', views.logout_view,
        name='rest__registration__logout'),
    url(r'^rest/registration/check/$', views.check_logged,
        name='rest__registration__checklogged'),
    url(r'^rest/registration/retrieveauthenticateduser/$',
        views.retrieve_authenticated_user,
        name='rest__registration__retrieveauthenticateduser'),
]

urlpatterns += pumpwoodrouter.urls
