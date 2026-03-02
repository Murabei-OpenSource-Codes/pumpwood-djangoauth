"""
Define configurations for Pumpwood systems and iniciate singletons objects.

It is used to centralize criation and inicialization of Pumpwood systens
singletons. These object are setted using enviroment variables and
can be imported at the through the application.

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
from pumpwood_miscellaneous.storage import PumpWoodStorage
from pumpwood_miscellaneous.rabbitmq import PumpWoodRabbitMQ
from pumpwood_kong.kong_api import KongAPI
from pumpwood_i8n.translate import PumpwoodI8n
from pumpwood_i8n.singletons import pumpwood_i8n
from diskcache import Cache

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
# Create an Kong api using API_GATEWAY_URL enviroment variable
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL")
kong_api: KongAPI = KongAPI(api_gateway_url=API_GATEWAY_URL)

######################################
# Microservice object inicialization #
# Getting secrets from enviroment variables
MICROSERVICE_NAME: str = os.environ.get("MICROSERVICE_NAME")
MICROSERVICE_URL: str = os.environ.get("MICROSERVICE_URL")
MICROSERVICE_USERNAME: str = os.environ.get("MICROSERVICE_USERNAME")
MICROSERVICE_PASSWORD: str = os.environ.get("MICROSERVICE_PASSWORD")
microservice: PumpWoodStorage = None
microservice_no_login: PumpWoodStorage = None
if MICROSERVICE_URL is not None:
    microservice_no_login = PumpWoodMicroService(
        name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
        verify_ssl=False)
    if MICROSERVICE_USERNAME is not None:
        microservice = PumpWoodMicroService(
            name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
            username=MICROSERVICE_USERNAME, password=MICROSERVICE_PASSWORD,
            verify_ssl=False)
else:
    print("PumpWoodMicroService not set")

##################
# Storage Object #
STORAGE_TYPE: str = os.environ.get('STORAGE_TYPE')
STORAGE_BUCKET_NAME: str = os.environ.get('STORAGE_BUCKET_NAME')
STORAGE_BASE_PATH: str = os.environ.get('STORAGE_BASE_PATH', 'pumpwood_auth')
storage_object = None
if STORAGE_TYPE is not None:
    storage_object = PumpWoodStorage(
        storage_type=STORAGE_TYPE, bucket_name=STORAGE_BUCKET_NAME,
        base_path=STORAGE_BASE_PATH)
else:
    print("PumpWoodStorage not set")


############
# RabbitMQ #
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', "5672"))
rabbitmq_api = None
if RABBITMQ_HOST is not None:
    rabbitmq_api = PumpWoodRabbitMQ(
        username=RABBITMQ_USERNAME, password=RABBITMQ_PASSWORD,
        host=RABBITMQ_HOST, port=RABBITMQ_PORT)
else:
    print("PumpWoodRabbitMQ not set")


#######
# I8n #
# Initiante I8n using django model as backend
pumpwood_i8n.init(microservice=microservice)

#########
# Cache #
# Create a diskcache object to cache row and API permission calls
# default size of 100Mb. It is restricted to not consume K8s cluster too
# much disk at PODs
DISKCACHE_EXPIRATION = os.getenv(
    'DISKCACHE__SIZELIMIT_MB', 100) * 1024 * 1024
diskcache = Cache(size_limit=DISKCACHE_EXPIRATION)
"""Diskcache object that can be used to cache request persistent
   information. Exemples of this is Pumpwood row and API permission."""

# Default 1 minute for cache expiration
DISKCACHE_EXPIRATION = os.getenv('DISKCACHE__EXPIRATION', 60)
"""Default time for diskcach expiration."""


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
