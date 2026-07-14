"""Pumpwood system models and views for Kong service mesh metadata.

Provides ``KongService`` and ``KongRoute`` models, serializers and REST
views used to register and list microservice routes. Add
``pumpwood_djangoauth.system`` to ``INSTALLED_APPS`` and include
``pumpwood_djangoauth.system.urls`` under ``/rest/``.
"""
