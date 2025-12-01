"""Create an admin site using MFAAdmin."""
from django.contrib import admin
from pumpwood_djangoauth.mfaadmin.views import MFALoginView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.http import HttpResponseRedirect
from django.urls import reverse
from pumpwood_djangoauth.mfaadmin.forms import MFAAuthenticationForm
from django.utils.translation import gettext as _


class MFAAdmin(admin.AdminSite):
    login_template = "mfa_login.html"
    login_form = MFAAuthenticationForm

    @method_decorator(never_cache)
    def login(self, request, extra_context=None):
        """Display the login form for the given HttpRequest."""
        if request.method == 'GET' and self.has_permission(request):
            # Already logged-in, redirect to admin index
            index_path = reverse('admin:index', current_app=self.name)
            return HttpResponseRedirect(index_path)

        # Since this module gets imported in the application's root package,
        # it cannot import models from other applications at the module level,
        # and django.contrib.admin.forms eventually imports User.
        context = {
            **self.each_context(request),
            'title': _('Log in'),
            'app_path': request.get_full_path(),
            'username': request.user.get_username(),
        }
        if (REDIRECT_FIELD_NAME not in request.GET and
                REDIRECT_FIELD_NAME not in request.POST):
            context[REDIRECT_FIELD_NAME] = \
                reverse('admin:index', current_app=self.name)
        context.update(extra_context or {})

        defaults = {
            'extra_context': context,
            'authentication_form': self.login_form,
            'template_name': self.login_template}
        request.current_app = self.name
        return MFALoginView.as_view(**defaults)(request)
