from django.urls import path
from pumpwood_djangoauth.mfaadmin.views import MFATokenValidationView


urlpatterns = [
    # Login/out end-points
    path(
        'mfa-token-validation/', MFATokenValidationView.as_view(),
        name='mfa-token-validation'),
]
