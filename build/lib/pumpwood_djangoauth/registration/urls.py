from pumpwood_djangoviews.routers import PumpWoodRouter
from django.conf.urls import url
from pumpwood_djangoauth.registration import views
from pumpwood_djangoauth.registration.mfa_aux.views import oauth2, code
from knox import views as knox_views

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestUser)

urlpatterns = [
    # Login/out end-points
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

    # MFA end-points
    url(r'^rest/registration/mfa-list-user-methods/$',
        views.get_user_mfa_methods,
        name='rest__registration__mfa_list_user_methods'),

    # MFA code end-points
    url(r'^rest/registration/mfa-generate-code/(?P<pk>\d+)/$',
        code.create_new_mfa_code,
        name='rest__registration__mfa_code_generate_code'),
    url(r'^rest/registration/mfa-validate-code/$',
        code.MFALoginView.as_view(),
        name='rest__registration__mfa_code_validate_code'),

    # MFA SSO OAuth2 End-points
    url(r'^rest/registration/oauth2-login/$',
        oauth2.oauth2_get_authorization_url,
        name='rest__registration__mfa_oauth2_login'),
    url(r'^rest/registration/oauth2-callback/$',
        oauth2.SSOLoginView.as_view(),
        name='rest__registration__mfa_oauth2_callback'),
]

urlpatterns += pumpwoodrouter.urls
