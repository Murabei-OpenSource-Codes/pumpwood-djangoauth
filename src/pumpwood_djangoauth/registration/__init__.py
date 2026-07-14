"""User registration, authentication, MFA and SSO end-points.

Provides ``UserProfile``, login and logout views, MFA token validation and
OAuth2/SSO flows. Add ``pumpwood_djangoauth.registration`` to
``INSTALLED_APPS`` and include ``pumpwood_djangoauth.registration.urls``
under ``/rest/``.

Environment variables for MFA and SSO are documented in the package README
and in ``pumpwood_djangoauth.config``.
"""
