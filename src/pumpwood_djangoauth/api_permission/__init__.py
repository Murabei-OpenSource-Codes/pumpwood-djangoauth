"""API permission models and end-points for Pumpwood Auth.

Defines policies, actions and group/user associations that control access
to Pumpwood REST end-points. Policies and actions expose an optional unique
``code`` field for stable identification across environments.

Usage:
    Add ``pumpwood_djangoauth.api_permission`` to ``INSTALLED_APPS`` and
    include ``pumpwood_djangoauth.api_permission.urls`` under ``/rest/``.
"""
