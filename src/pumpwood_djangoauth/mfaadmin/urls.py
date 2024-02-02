from django.conf.urls import url
from pumpwood_djangoauth.mfaadmin.views import MFATokenValidationView


urlpatterns = [
    # Login/out end-points
    url(r'mfa-token-validation/', MFATokenValidationView.as_view(),
        name='mfa-token-validation'),
]
