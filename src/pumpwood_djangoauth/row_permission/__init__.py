"""Row permission models, serializers and REST views for Pumpwood Auth.

Defines ``PumpwoodRowPermission`` tags and their associations with user
groups and individual users. Row permissions restrict retrieve, list and
aggregate queries through ``base_query``. Each tag may expose an optional
unique ``code`` field for stable identification.

Usage:
    Add ``pumpwood_djangoauth.row_permission`` to ``INSTALLED_APPS`` and
    include ``pumpwood_djangoauth.row_permission.urls`` under ``/rest/``.
"""
