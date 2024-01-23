"""Views for MFA Autentication."""
from django.conf import settings
from django.urls import reverse
from django.shortcuts import resolve_url
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.cache import never_cache
from pumpwood_djangoauth.mfaadmin.forms import (
    MFAAuthenticationForm, MFATokenValidationForm)


class MFALoginView(LoginView):
    """
    Custom login view that will generate a MFA Code.

    It will generate MFA Method.
    """

    form_class = MFAAuthenticationForm
    template_name = 'admin/mfa_login.html'

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        """."""
        # Check if user is Autenticated and redirect
        is_authenticated = (
            self.redirect_authenticated_user and
            self.request.user.is_authenticated)
        if is_authenticated:
            redirect_to = self.get_success_url()
            if redirect_to == self.request.path:
                error_msg = (
                    "Redirection loop for authenticated user detected. "
                    "Check that your LOGIN_REDIRECT_URL doesn't point to a "
                    "login page.")
                raise ValueError(error_msg)
            return HttpResponseRedirect(redirect_to)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """."""
        # If mfa_token is returned from form, then redirect user to
        # MFA token validation
        mfa_token = form.cleaned_data.get("mfa_token")
        mfa_token_expiry = form.cleaned_data.get("expiry")
        if mfa_token is not None:
            validation_url = reverse('mfa-token-validation')
            response = HttpResponseRedirect(validation_url)

            # Set mfa_token to user COOKIES, it will be used latter
            # at 'mfa-token-validation' to get logged user.
            response.set_cookie('mfa_token', mfa_token)
            response.set_cookie('mfa_token_expiry', mfa_token_expiry)
            return response
        return super().form_valid(form)


class MFATokenValidationView(FormView):
    """View to validate MFA Code using MFA token as autorization."""

    template_name = "mfa_token_validation.html"
    form_class = MFATokenValidationForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        """."""
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """."""
        kw = super(MFATokenValidationView, self).get_form_kwargs()

        # Pass request to form to get mfa_token at cookies
        kw['request'] = self.request
        return kw

    def get_success_url(self):
        """."""
        # If form does not have errors then redirect to admin:index
        success_url = reverse('admin:index')
        return resolve_url(success_url)

    def form_valid(self, form):
        """."""
        # Form returns the logged user using mfa_token generated on
        # login view, if not errors are raised then the MFA code is valid
        # and MFA token is correct, user will be logged.
        user = form.cleaned_data["user"]
        login(self.request, user)
        return super().form_valid(form)
