"""Registration URLs."""
from django.urls import path
from knox import views as knox_views
from pumpwood_djangoviews.routers import PumpWoodRouter
from pumpwood_djangoauth.registration import views
from pumpwood_djangoauth.registration.mfa_aux.views import oauth2, code

pumpwoodrouter = PumpWoodRouter()
pumpwoodrouter.register(viewset=views.RestUser)
pumpwoodrouter.register(viewset=views.RestUserProfile)


urlpatterns = [
    # Login/out end-points
    path(
        'rest/registration/login/', views.LoginView.as_view(),
        name='rest__registration__login'),
    path(
        'rest/registration/logout/', knox_views.LogoutView.as_view(),
        name='rest__registration__logout'),
    path(
        'rest/registration/logoutall/', knox_views.LogoutAllView.as_view(),
        name='rest__registration__logoutall'),
    path(
        'rest/registration/check/', views.CheckAuthentication.as_view(),
        name='rest__registration__checklogged'),
    path(
        'rest/registration/retrieveauthenticateduser/',
        views.retrieve_authenticated_user,
        name='rest__registration__retrieveauthenticateduser'),

    # MFA end-points
    path(
        'rest/registration/mfa-list-user-methods/',
        views.get_user_mfa_methods,
        name='rest__registration__mfa_list_user_methods'),

    # MFA code end-points
    path(
        'rest/registration/mfa-generate-code/<int:pk>/',
        code.create_new_mfa_code,
        name='rest__registration__mfa_code_generate_code'),
    path(
        'rest/registration/mfa-validate-code/',
        code.MFALoginView.as_view(),
        name='rest__registration__mfa_code_validate_code'),

    # MFA SSO OAuth2 End-points
    path(
        'rest/registration/oauth2-login/',
        oauth2.oauth2_get_authorization_url,
        name='rest__registration__mfa_oauth2_login'),
    path(
        'rest/registration/oauth2-callback/',
        oauth2.SSOLoginView.as_view(),
        name='rest__registration__mfa_oauth2_callback'),
]

urlpatterns += pumpwoodrouter.urls
