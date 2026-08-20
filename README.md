# PumpWood Django Auth

Create basic Pumpwood end-points for authentication and service mesh using
Kong. It integrates with
<a href="https://github.com/Murabei-OpenSource-Codes/pumpwood-communication">
    pumpwood-communication
</a> and
<a href="https://github.com/Murabei-OpenSource-Codes/pumpwood-djangoviews">
    pumpwood-djangoviews
</a>.

<p align="center" width="60%">
  <img src="static_doc/sitelogo-horizontal.png" /> <br>

  <a href="https://en.wikipedia.org/wiki/Cecropia">
    Pumpwood is a native Brazilian tree
  </a> which has a symbiotic relation with ants (Murabei)
</p>

## Objective and motivation

Pumpwood Django Auth is the authentication and authorization service for
the Pumpwood stack. It exposes user registration, MFA and SSO login, API
permission policies, row permissions, and Kong route registration.

### Why this exists

It centralizes auth, permission checks, and service-mesh route metadata
so consumer applications integrate through one Django package.

### How it is used

Deploy as the ``pumpwood-auth-app`` image. Frontends and workers call
``/rest/registration/`` for login, token validation, and permission
endpoints. Service users authenticate in-cluster; external login is
blocked for them.

### Scope

Owns users, profiles, groups, API and row permissions, and Kong sync.
Business-domain models live in consuming applications.

Licensed under BSD-3-Clause (see ``pyproject.toml``).

## Environment variables

The `config` module centralizes singletons used across Pumpwood Auth.
Network and disk clients are wrapped in ``LazyProxy`` and created on first
use. When running gunicorn with ``--preload``, call
``reset_config_singletons()`` from a ``post_fork`` hook so workers do not
reuse master-process connections.

### Kong integration

- `API_GATEWAY_URL`: Kong admin API host. Required to register services and
  routes through ``KongService`` and ``KongRoute`` models.

### Pumpwood microservice integration

- `MICROSERVICE_NAME`: microservice object name, used for debug purposes.
- `MICROSERVICE_URL`: full path of the Pumpwood API Gateway or service mesh.
- `MICROSERVICE_USERNAME`: username used for service-to-service login.
- `MICROSERVICE_PASSWORD`: password used for service-to-service login.

Service users flagged with ``UserProfile.is_service_user`` cannot log in from
outside the application cluster.

### Pumpwood storage integration

- `STORAGE_TYPE`: storage back-end
  [``google_bucket``, ``aws_s3``, ``azure_storage``].
- `STORAGE_BUCKET_NAME`: name of the bucket, blob or S3 to be used.
- `STORAGE_BASE_PATH`: base path when saving files. Defaults to
  ``pumpwood_auth``.
- `MEDIA_URL`: media base URL for Kong routes. Defaults to ``media/``.

#### Pumpwood storage cloud configuration

Depending on the storage back-end, credentials and other information must be
provided.

- aws_s3
  - `AWS_ACCESS_KEY_ID`: access key for the service user to access S3.
  - `AWS_SECRET_ACCESS_KEY`: secret key for the service user to access S3.
- azure_storage
  - `AZURE_STORAGE_CONNECTION_STRING`: connection string for the storage
    account.
- google_bucket
  - `GOOGLE_APPLICATION_CREDENTIALS`: path to Google application credentials.

### RabbitMQ logging

- `RABBITMQ_USERNAME`, `RABBITMQ_PASSWORD`, `RABBITMQ_HOST`,
  `RABBITMQ_PORT`: credentials and host for RabbitMQ log delivery.
- `PUMPWOOD_AUTH_IS_RABBITMQ_LOG` [``TRUE``, ``FALSE``]: send authentication
  logs to RabbitMQ (``TRUE``) or stdout (``FALSE``). When ``TRUE`` but
  RabbitMQ credentials are missing, logs fall back to stdout.

All calls with the ``X-PUMPWOOD-Ingress-Request`` header (set by an NGINX
termination container) whose user is not a service user are sent to the
``auth__api_request_log`` queue.

### Cache expiration

- `PUMPWOOD_AUTH__I8N_CACHE_EXPIRATION`: i18n cache TTL in seconds. Default
  ``300``.
- `PUMPWOOD_AUTH__TOKEN_CACHE_EXPIRATION`: permission token cache TTL.
  Default ``300``.
- `PUMPWOOD_AUTH__ROW_PERMISSION_CACHE_EXPIRATION`: row permission cache TTL.
  Default ``300``.

## Quick start

Add Pumpwood Auth apps to ``settings.py``:

```
INSTALLED_APPS = [
    # Admin APPs
    'flat_json_widget',
    'pumpwood_djangoviews',

    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_extensions',

    # MFA Admin
    'rest_framework',
    'knox',

    # Django Pumpwood Auth Models
    'pumpwood_djangoauth',
    'pumpwood_djangoauth.i8n',
    'pumpwood_djangoauth.mfaadmin',
    'pumpwood_djangoauth.registration',
    'pumpwood_djangoauth.system',
    'pumpwood_djangoauth.groups',
    'pumpwood_djangoauth.row_permission',
    'pumpwood_djangoauth.api_permission',
]
```

Add request logging middleware (login must be the last middleware call):

```
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'pumpwood_djangoauth.log.middleware.RequestLogMiddleware',
]
```

Configure REST framework and Knox:

```
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'knox.auth.TokenAuthentication',
    ),
    'EXCEPTION_HANDLER': (
        'pumpwood_djangoviews.exception_handler.custom_exception_handler'
    )
}
```

Add routes to ``urls.py``. You can include each app separately or use the
consolidated entry point:

```
urlpatterns = [
    url(r'^health-check/pumpwood-auth-app/',
        lambda r: JsonResponse(True, safe=False)),
    url(r'^rest/', include('pumpwood_djangoauth.urls')),
]
```

### Login response

Successful password, MFA code, and SSO login return a Knox token plus a
full ``SerializerUser`` payload when ``foreign_key_fields`` and
``related_fields`` are enabled. The ``user`` object includes Django
permission codenames (``all_permissions``, ``group_permissions``),
``user_group_m2m_set``, and a nested ``user_profile`` with effective
permissions:

- ``user_profile.self_api_permissions`` — merged API route access from
  direct and group links (via ``UserProfile.user_api_permissions``).
- ``user_profile.self_row_permissions`` — merged row-permission records
  (via ``UserProfile.user_row_permissions``).

Pass ``context={'request': request}`` when serializing so profile
permission fields resolve. ``retrieve_authenticated_user`` follows the
same pattern.

### Gunicorn preload

When using gunicorn with ``--preload``, reset lazy singletons after fork:

```
def post_fork(server, worker):
    from pumpwood_djangoauth.config import reset_config_singletons
    reset_config_singletons()
```

### Permission codes

Groups, row permissions and API permission policies expose a ``code`` field
for stable identification across environments and integrations.

- `PumpwoodUserGroup.code`: required, unique identifier for a permission
  group.
- `PumpwoodRowPermission.code`: optional, unique identifier for a row
  permission tag.
- `PumpwoodPermissionPolicy.code`: optional, unique identifier for an API
  permission policy.
- `PumpwoodPermissionPolicyAction.code`: optional, unique identifier for a
  policy action.

Codes are available on REST serializers and can be used when linking policies
programmatically instead of relying on database primary keys.

### Registering end-points

Use ``register_auth_kong_objects`` to register services and routes at Kong.
For the default auth layout, ``get_service_definitions`` from
``pumpwood_djangoauth.service_registration`` returns ready-made service and
route dictionaries.

```
from pumpwood_djangoauth.kong.create_routes import register_auth_kong_objects
from pumpwood_djangoauth.service_registration import get_service_definitions
from pumpwood_djangoauth.system.views import (
    RestKongRoute, RestKongService)
from pumpwood_djangoauth.registration.views import RestUser

service_url = os.environ.get("SERVICE_URL")

register_auth_kong_objects(
    service_url=service_url,
    service_name="people-and-cats-main",
    healthcheck_route="/health-check/pumpwood-auth-app/",
    service_description="Main auth application",
    service_notes="Main app.",
    service_dimensions={
        "microservice": "pumpwood-auth-app",
        "type": "core",
        "function": "authentication"},
    service_icon=None,
    service_extra_info={},
    routes=[{
        "route_url": "/rest/registration/",
        "route_name": "api--registration",
        "route_type": "aux",
        "description": "Registration",
        "notes": (
            "End-point for login, logout and other Authentication "
            "functions"),
        "dimensions": {
            "microservice": "pumpwood-auth-app",
            "service_type": "core",
            "function": "authentication",
            "endpoint": "registration",
            "route_type": "aux"},
        "icon": "",
        "extra_info": {}
    }],
    viewsets=[RestKongRoute, RestKongService, RestUser])
```

### Login MFA

- `PUMPWOOD__MFA__TOKEN_EXPIRATION_INTERVAL`: MFA token expiration in
  seconds.
- `PUMPWOOD__MFA__APPLICATION_NAME`: application name used on MFA messages.

### Twilio SMS

- `PUMPWOOD__MFA__TWILIO_ACCOUNT_SID`: Twilio Account SID.
- `PUMPWOOD__MFA__TWILIO_AUTH_TOKEN`: Twilio Auth Token.

### Single sign-on (SSO)

- `PUMPWOOD__SSO__PROVIDER`: SSO provider. Supported value:
  ``microsoft-entra``.
- `PUMPWOOD__SSO__REDIRECT_URL`: redirect URL after SSO login.
- `PUMPWOOD__SSO__AUTHORIZATION_URL`: authorization URL for SSO login.
- `PUMPWOOD__SSO__TOKEN_URL`: token URL for SSO login.
- `PUMPWOOD__SSO__CLIENT_ID`: OAuth client ID (Entra).
- `PUMPWOOD__SSO__SECRET`: OAuth client secret (Entra).
- `PUMPWOOD__SSO__SCOPE`: JSON list of OAuth scopes. Default
  ``["openid", "profile", "email"]``.
- `PUMPWOOD__SSO__PROXY_HTTP` and `PUMPWOOD__SSO__PROXY_HTTPS`: optional
  HTTP/HTTPS proxies for SSO requests. Both must be set when using proxies.
