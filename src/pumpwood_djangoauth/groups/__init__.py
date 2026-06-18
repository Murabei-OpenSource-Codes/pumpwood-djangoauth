"""User group models, serializers and REST views for Pumpwood Auth.

Provides ``PumpwoodUserGroup`` and ``PumpwoodUserGroupM2M`` to organize
users and apply API and row permission policies. Each group exposes a
unique ``code`` field for stable identification across environments.

Usage:
    Add ``pumpwood_djangoauth.groups`` to ``INSTALLED_APPS`` and include
    ``pumpwood_djangoauth.groups.urls`` under ``/rest/``.
"""
