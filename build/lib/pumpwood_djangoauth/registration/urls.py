from pumpwood_djangoviews.routers import PumpWoodRouter
from django.conf.urls import url
from pumpwood_djangoauth.registration import views
from knox import views as knox_views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestUser)

urlpatterns = [
    url(r'^rest/registration/login/$', views.LoginView.as_view(),
        name='rest__registration__login'),
    url(r'^rest/registration/logout/$', knox_views.LogoutView.as_view(),
        name='rest__registration__logout'),
    url(r'^rest/registration/logoutall/$', knox_views.LogoutAllView.as_view(),
        name='rest__registration__logoutall'),
    url(r'^rest/registration/check/$', views.CheckAuthentication.as_view(),
        name='rest__registration__checklogged'),
    url(r'^rest/registration/retrieveauthenticateduser/$',
        views.retrieve_authenticated_user,
        name='rest__registration__retrieveauthenticateduser'),
]

urlpatterns += pumpwoodrouter.urls
