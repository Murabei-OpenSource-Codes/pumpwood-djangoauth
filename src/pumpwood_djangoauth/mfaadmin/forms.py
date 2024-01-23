"""Create custom login form."""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate, login
from django.utils import timezone
from pumpwood_djangoauth.registration.models import PumpwoodMFAToken
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class MFAAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username is not None and password:
            self.user_cache = authenticate(
                username=username, password=password)
            if self.user_cache is None:
                raise self.get_invalid_login_error()

            self.confirm_login_allowed(self.user_cache)
            priority_mfa = self.user_cache.mfa_method_set.\
                order_by('priority').first()
            is_service_user = self.user_cache.user_profile.is_service_user
            if (priority_mfa is not None) and (not is_service_user):
                new_mfa_token = self.create_mfa_token(
                    user=self.user_cache, priority_mfa=priority_mfa)
                self.cleaned_data = new_mfa_token
                return self.cleaned_data
            else:
                return self.cleaned_data

    def create_mfa_token(self, user, priority_mfa):
        """
        Create an MFA token.

        user [User]: Autenticated user.
        """
        from pumpwood_djangoauth.registration.models import (
            PumpwoodMFAToken, PumpwoodMFACode)
        new_mfa_token = PumpwoodMFAToken(user=user)
        new_mfa_token.save()

        # Create MFA token using primary mfa
        mfa_code = PumpwoodMFACode(
            token=new_mfa_token, mfa_method=priority_mfa)
        mfa_code.save()
        return {
            'expiry': new_mfa_token.expire_at,
            'mfa_token': new_mfa_token.token}


class MFATokenValidationForm(forms.Form):
    mfa_code = forms.CharField(max_length=6)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        mfa_token = self.request.COOKIES.get('mfa_token')
        mfa_token_obj = PumpwoodMFAToken.objects.\
            filter(token=mfa_token).first()

        if mfa_token_obj is None:
            raise ValidationError(
                _("MFA Token is incorrect, please login again."))

        now = timezone.now()
        if mfa_token_obj.expire_at < now:
            raise ValidationError(_("MFA Token is expired"))

        mfa_code = self.cleaned_data.get('mfa_code')
        code_obj = mfa_token_obj.mfa_code_set.filter(
            code=mfa_code).first()
        if code_obj is None:
            raise ValidationError(_("MFA Code is incorrect"))

        self.cleaned_data = {
            "mfa_token_obj": mfa_token_obj,
            "user": mfa_token_obj.user,
            "code_obj": code_obj}
        return self.cleaned_data
