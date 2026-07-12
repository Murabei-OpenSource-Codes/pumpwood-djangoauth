"""
Define configurations for Pumpwood systems and iniciate singletons objects.

It is used to centralize criation and inicialization of Pumpwood systens
singletons. These object are setted using enviroment variables and
can be imported at the through the application.

Network and disk singletons are wrapped in ``LazyProxy`` so they are
created on first use. This avoids opening shared sockets during gunicorn
``--preload`` and keeps initialization thread-safe under ``gthread``
workers. Call ``reset_config_singletons()`` from a gunicorn ``post_fork``
hook when using preload.

Example of usage:
```python
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.config import (
    storage_object, microservice, rabbitmq_api)
from .models import NiceEndPoint
from .serializers import NiceEndPointSerializer

class RestNicePumpwoodEndPoint(PumpWoodRestService):
    endpoint_description = "Nice End-point"
    notes = "This is a super nice pumpwood end-point"

    service_model = NiceEndPoint
    serializer = NiceEndPointSerializer

    # Uses singletons storage_object and microservice that
    # were iniciated using enviroment variables
    storage_object = storage_object
    microservice = microservice
```
"""
import os
from pumpwood_communication.microservices import PumpWoodMicroService
from pumpwood_communication.cache import default_cache
from pumpwood_miscellaneous.storage import PumpWoodStorage
from pumpwood_miscellaneous.rabbitmq import PumpWoodRabbitMQ
from pumpwood_kong.kong_api import KongAPI
from pumpwood_i8n.translate import PumpwoodI8n
from pumpwood_i8n.singletons import pumpwood_i8n as _pumpwood_i8n_singleton
from pumpwood_djangoauth.lazy_proxy import LazyProxy
from pumpwood_djangoauth.aux.general import django_apps_ready


#####################
# Singleton objects #
kong_api: KongAPI
"""Singleton used by Pumpwood Auth to register services and routes at Kong Api
   service mesh. It will be used enviroment variable `API_GATEWAY_URL` to
   initialize this object."""
microservice: PumpWoodMicroService
"""
Singleton used by Pumpwood Auth to request call other microservices. It will
be used `MICROSERVICE_NAME`, `MICROSERVICE_URL`, `MICROSERVICE_USERNAME`
and `MICROSERVICE_PASSWORD` enviroment variable to initialize this object.

It is possible to use microservice to call pumpwood auth information, **just
be carefull with recursive calls that will break the backend**.

**It is not recomended to use recursive calls at system startup**, this migth
make system unavaiable (None replica will be avaiable to repond recursive
call.).
"""
microservice_no_login: PumpWoodMicroService
"""
Singleton used by Pumpwood Auth to request call other microservices. This
object will not be logged using `MICROSERVICE_USERNAME` and
`MICROSERVICE_PASSWORD` enviroment variables. It can be used to impersonate
user when requesting other microservices.
"""
storage_object: PumpWoodStorage
"""
Singleton used to comunicate with flat storage. It is used
`STORAGE_TYPE`, `STORAGE_BUCKET_NAME`, `STORAGE_BASE_PATH` for this
object inicialization.
"""
rabbitmq_api: PumpWoodRabbitMQ
"""
Singleton used to comunicate with RabbitMQ. It is used
`RABBITMQ_USERNAME`, `RABBITMQ_PASSWORD`, `RABBITMQ_HOST` and `RABBITMQ_PORT`
for this object inicialization.
"""
PUMPWOOD_AUTH_IS_RABBITMQ_LOG: str = os.getenv(
    'PUMPWOOD_AUTH_IS_RABBITMQ_LOG', "FALSE") == 'TRUE'
"""Will set if logs should be dumped to RabbitMQ or printed to stdout."""
pumpwood_i8n: PumpwoodI8n
"""
Singleton imported from `pumpwood_i8n.singletons`, it is used to translate
sentences using Pumpwood I8s end-points.
"""
MEDIA_URL: str = os.environ.get('MEDIA_URL', 'media/')
"""Media base URL it can be used to create routes on Kong and make media
   end-points avaiable at app URLs. Default value can be changed using
   enviroment variable `MEDIA_URL`"""

###################################
# Kong interaction inicialization #
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL")

######################################
# Microservice object inicialization #
MICROSERVICE_NAME: str = os.environ.get("MICROSERVICE_NAME")
MICROSERVICE_URL: str = os.environ.get("MICROSERVICE_URL")
MICROSERVICE_USERNAME: str = os.environ.get("MICROSERVICE_USERNAME")
MICROSERVICE_PASSWORD: str = os.environ.get("MICROSERVICE_PASSWORD")

##################
# Storage Object #
STORAGE_TYPE: str = os.environ.get('STORAGE_TYPE')
STORAGE_BUCKET_NAME: str = os.environ.get('STORAGE_BUCKET_NAME')
STORAGE_BASE_PATH: str = os.environ.get('STORAGE_BASE_PATH', 'pumpwood_auth')

############
# RabbitMQ #
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', "5672"))

#########
# Cache #
I8N_CACHE_EXPIRATION = int(
    os.getenv('PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION', '300'))
"""Default time for i8n cache expiration."""


def _build_kong_api():
    """Build Kong API client from enviroment variables."""
    return KongAPI(api_gateway_url=API_GATEWAY_URL)


def _build_microservice_no_login():
    """Build microservice client without login credentials."""
    if MICROSERVICE_URL is None:
        return None
    return PumpWoodMicroService(
        name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
        verify_ssl=False)


def _build_microservice():
    """Build microservice client with login credentials."""
    if MICROSERVICE_URL is None or MICROSERVICE_USERNAME is None:
        return None
    return PumpWoodMicroService(
        name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
        username=MICROSERVICE_USERNAME, password=MICROSERVICE_PASSWORD,
        verify_ssl=False)


def _build_storage_object():
    """Build flat storage client from enviroment variables."""
    if STORAGE_TYPE is None:
        return None
    return PumpWoodStorage(
        storage_type=STORAGE_TYPE, bucket_name=STORAGE_BUCKET_NAME,
        base_path=STORAGE_BASE_PATH)


def _build_rabbitmq_api():
    """Build RabbitMQ client from enviroment variables."""
    if RABBITMQ_HOST is None:
        return None
    return PumpWoodRabbitMQ(
        username=RABBITMQ_USERNAME, password=RABBITMQ_PASSWORD,
        host=RABBITMQ_HOST, port=RABBITMQ_PORT)


def _build_pumpwood_i8n():
    """Initiante I8n using django model as backend."""
    _pumpwood_i8n_singleton.init(
        pumpwood_cache=default_cache,
        i8n_model='pumpwood_djangoauth.i8n.models.PumpwoodI8nTranslation',
        app_ready_check=django_apps_ready)
    return _pumpwood_i8n_singleton


kong_api = LazyProxy(_build_kong_api)
microservice_no_login = LazyProxy(_build_microservice_no_login)
microservice = LazyProxy(_build_microservice)
storage_object = LazyProxy(_build_storage_object)
rabbitmq_api = LazyProxy(_build_rabbitmq_api)
pumpwood_i8n = LazyProxy(_build_pumpwood_i8n)

_LAZY_SINGLETONS = (
    kong_api, microservice_no_login, microservice, storage_object,
    rabbitmq_api, pumpwood_i8n)


def reset_config_singletons():
    """Reset lazy singletons after gunicorn worker fork.

    Call this function from a gunicorn ``post_fork`` hook when using
    ``--preload`` so workers do not reuse master-process connections.
    """
    for proxy in _LAZY_SINGLETONS:
        proxy.reset()


PUMPWOOD__AUTH__TOKEN_CACHE_EXPIRE = int(os.getenv(
    'PUMPWOOD__AUTH__PERMISSION_CACHE_EXPIRE', 300))
"""Time to set expire at permission cache."""

#####################
# SSO configuration #
PUMPWOOD__SSO__REDIRECT_URL = os.getenv(
    "PUMPWOOD__SSO__REDIRECT_URL")
"""Set a redirect URL after SSO login."""
PUMPWOOD__SSO__AUTHORIZATION_URL = os.getenv(
    "PUMPWOOD__SSO__AUTHORIZATION_URL")
"""Authorization URL SSO login."""
PUMPWOOD__SSO__TOKEN_URL = os.getenv(
    "PUMPWOOD__SSO__TOKEN_URL")
"""Token URL SSO login."""
PUMPWOOD__SSO__CLIENT_ID = os.getenv(
    "PUMPWOOD__SSO__CLIENT_ID")
"""Token URL SSO CIENT_ID (Entra)."""
PUMPWOOD__SSO__SECRET = os.getenv(
    "PUMPWOOD__SSO__SECRET")
"""Token URL SSO CIENT_ID (Entra)."""
PUMPWOOD__SSO__SCOPE = os.getenv(
    "PUMPWOOD__SSO__SCOPE", '["openid", "profile", "email"]')
"""Set the SCOPE of the SSO request, it is a JSON list of strings."""
PUMPWOOD__SSO__PROXY_HTTP = os.getenv(
    "PUMPWOOD__SSO__PROXY_HTTP")
"""Set HTTP proxy to be used to make the SSO requests."""
PUMPWOOD__SSO__PROXY_HTTPS = os.getenv(
    "PUMPWOOD__SSO__PROXY_HTTPS")
"""Set HTTPS proxy to be used to make the SSO requests."""


SSO_PROXY_CONFIG = None
if PUMPWOOD__SSO__PROXY_HTTP is not None:
    if PUMPWOOD__SSO__PROXY_HTTPS is None:
        msg = (
            "If set both proxy must be set _PUMPWOOD__SSO__PROXY_HTTP and "
            "_PUMPWOOD__SSO__PROXY_HTTPS")
        raise Exception(msg)
    SSO_PROXY_CONFIG = {
        'http': PUMPWOOD__SSO__PROXY_HTTP,
        'https': PUMPWOOD__SSO__PROXY_HTTPS,
    }
