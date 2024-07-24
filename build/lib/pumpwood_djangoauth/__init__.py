"""
# Pumpwood models for auth and internals.

Pumpwood Django Auth implements base models for Pumpwood systems. It is
implemented models that perform authetication, MFA validation, Kong service
mesh integration, logs generation and Metabase dashboard deploy.

## Enviroment variables
`config` modele is reponsible for defining singletons that are used through
pumpwood auth for rabbitmq, other pumpwood microservice and storage connection.
It also defines an object kong interaction that can be set as None during
app development.

- **API_GATEWAY_URL:** Correpond to Kong admin end-point. It is used to
    register new services and routes for auth and other microservice using
    `KongService` and `KongRoute` model class. Ex.:
    `http://load-balancer:8001/` when kong is deployed locally as
    `load-balancer` on docker-compose.
- **MICROSERVICE_NAME:** It is a default name for microservice that is
  used by app to comunicate with other microservices. This string is usually
  used for debug purposes and does not modify behavior of the application.
  Ex.: `microservice-auth`.
- **MICROSERVICE_URL:** Url of Kong end-point that redirect requests to other
    microservices. Ex.: `http://load-balancer:8000/` when Kong is deployed
    locally as `load-balancer`.
- **MICROSERVICE_USERNAME:** User name of the service user used by auth app
    to comunicate with other microservice. Ex.: `microservice--auth`.
    Users flaged as service users are not allowed to login from outside of the
    application cluster.
- **MICROSERVICE_PASSWORD:** Password associated with the service user used
    by application to communcati with other Pumpwood Microservice. It is a
    good pratice to set a strong password for service users, although they
    are not avaiable for login outside of the cluster.
- **STORAGE_TYPE:** Storage type that will be used store flat files on buckets,
    S3 or blob storage. Today it is possible to use `google_bucket`,
    `aws_s3` or `azure_storage`, for more information check documentation
    of `pumpwood_miscellaneous` package.
- **STORAGE_BUCKET_NAME:** Name of the bucket, blob storage or S3. For more
    information check  documentation of `pumpwood_miscellaneous` package.
- **STORAGE_BASE_PATH='pumpwood_auth':** Base path that will be used to store
    information on flat storage. If not set `pumpwood_auth`, there is
    usually no need to set a different value.
- **MEDIA_URL:** It is the default media path URL. It is used to set a route
    for media end-point on Pumpwood. It is `media/` if not set, usually no
    need to change that.
- **PUMPWOOD_AUTH_IS_RABBITMQ_LOG=FALSE:** Set if RabbitMQ should be used to
    queue loging of pumpwood. If not set to 'TRUE' pumpwood auth will send
    Pumpwood logs to stdout.

## Usage
To use pumpwood auth it is necessary to correcly configure Django settings,
add routes to Kong and add end-point URLs to application.

### Django settings
To use Pumpwood Django Auth it is necessary to add models to installed
apps at settings and configure rest framework and knox settings
dictionary.

Pumpwood Auth uses knox to generate tokens for user authetication,
rest framework for end-points creation. It prefereble

#### INSTALLED_APPS
```python
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
    'pumpwood_djangoauth.metabase',
    'pumpwood_djangoauth.api_permission',
]
```

#### Logs MIDDLEWARE
```python
MIDDLEWARE = [
    # CORS
    'corsheaders.middleware.CorsMiddleware',

    # BASIC
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',

    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    # Login must be last call...
    'pumpwood_djangoauth.log.middleware.RequestLogMiddleware',
]
```

#### Config REST_FRAMEWORK
Ajust Knox configuration if necessary... but it is important to keep
`knox.auth.TokenAuthentication` as `DEFAULT_AUTHENTICATION_CLASSES`,
`rest_framework.permissions.IsAuthenticated` on `DEFAULT_PERMISSION_CLASSES`
and `pumpwood_djangoviews.exception_handler.custom_exception_handler` as
`EXCEPTION_HANDLER`.

```python
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

#### Config REST_KNOX
Ajust Knox configuration if necessary...
```python
REST_KNOX = {
    'SECURE_HASH_ALGORITHM': 'cryptography.hazmat.primitives.hashes.SHA512',
    'AUTH_TOKEN_CHARACTER_LENGTH': 64,
    'TOKEN_TTL': timedelta(hours=12),
    'USER_SERIALIZER': 'knox.serializers.UserSerializer',
    'TOKEN_LIMIT_PER_USER': None,
    'AUTO_REFRESH': False,
    'EXPIRY_DATETIME_FORMAT': api_settings.DATETIME_FORMAT,
}
```

### Register end-points on Kong
To register models and other end-points on Kong it is possible to use
`register_auth_kong_objects` helper function. For that it is necessary to
set `get_wsgi_application()` to iniciate application models before importing
views.

Usually `SERVICE_URL` and `AUTH_STATIC_SERVICE` are set as enviroment
variables. This might help when deploing application on K8s or docker-compose
when both services might have different configuration.

It might be interesting to set a enviroment variable (Ex. `CLOUD`)to set if
application should register end-points or not. This is usefull for local
tests of application for unitesting and development.

```
from django.core.wsgi import get_wsgi_application
from pumpwood_djangoauth.kong.create_routes import register_auth_kong_objects
from pumpwood_djangoauth.config import MEDIA_URL

is_cloud_deploy = os.environ.get("CLOUD", "FALSE") == "TRUE"
if is_cloud_deploy:
    if "core.wsgi" in sys.argv:
        print("#########################################")
        print("# Registering API end-points on kong... #")
        print("#########################################")
        get_wsgi_application()

        from pumpwood_djangoauth.system.views import (
            RestKongRoute, RestKongService)
        from pumpwood_djangoauth.registration.views import RestUser
        from pumpwood_djangoauth.metabase.views import (
            RestMetabaseDashboard, RestMetabaseDashboardParameter)
        from pumpwood_djangoauth.i8n.views import RestPumpwoodI8nTranslation
        from pumpwood_djangoauth.api_permission.views import (
            RestPumpwoodPermissionPolicy, RestPumpwoodPermissionPolicyAction,
            RestPumpwoodPermissionGroup, RestPumpwoodPermissionUserGroupM2M,
            RestPumpwoodPermissionPolicyGroupM2M,
            RestPumpwoodPermissionPolicyUserM2M)

        service_url = os.environ.get("SERVICE_URL")
        auth_static_service = os.environ.get("AUTH_STATIC_SERVICE")

        # Register rest end-points and admin
        register_auth_kong_objects(
            service_url=service_url,

            # Set a name for service associated with routes of pumpwood-auth
            service_name="pumpwood-auth-app",

            # Register a healthcheck route for aplication
            healthcheck_route="/health-check/pumpwood-auth-app/",

            # Service description must be unique over all pumpwood services
            service_description="Authentication Microservice",

            # Notes that will be avaiable when getting registered end-points
            # on Pumpwood
            service_notes=(
                "Microservice responsible for User's authentication and "
                "general Pumpwood systems end-points."),

            # Key/Value tags to help on organization of end-points
            service_dimensions={
                "microservice": "pumpwood-auth-app",
                "type": "core",
                "function": "authentication"},

            # A icon (string associated with an icon) can be setted to help
            # rendering of side bar by frontend.
            service_icon=None,

            # Some extra info can be saved among with service information,
            # usually this information migth be usefull for programatic
            # consumption of the service by frontend.
            service_extra_info={},

            # List routes that should be registered at Kong associated with
            # this service. This is usefull for some routes are not associated
            # with models such as login routes, MFA validation, etc...
            routes=[{
                # Url associated with the route
                "route_url": "/rest/registration/",
                # Name of the route, it must be unique over all Pumpwood
                # system
                "route_name": "api--registration",

                # Type of the route, it must be in values `['endpoint',
                # 'aux', 'gui', 'datavis', 'static', 'admin', 'media']`. For
                # more information abount the options check
                # `systems.KongRoute.route_type` attribute options.
                "route_type": "aux",

                # User readble description of the route, it must be unique
                # over all pumpwood system.
                "description": "Registration",

                # A longer description for the end-point, this information
                # will be avaiable to front-end at list registred end-point.
                "notes": (
                    "End-point for login, logout and other Authentication "
                    "functions"),

                # Key/Values tag that will help to better organization of the
                # routes
                "dimensions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "authentication",
                    "endpoint": "registration",
                    "route_type": "aux"},

                # A string that can be associated with an icon, this is passed
                # to frontend and list registred end-point.
                "icon": "",

                # Dictionary that can be used to store information that can
                # be consumed programatic.
                "extra_info": {}
            }, {
                "route_url": "/rest/pumpwood/",
                "route_name": "api--pumpwood",
                "route_type": "aux",
                "description": "Pumpwood System",
                "notes": (
                    "System related end-points to list Kong routes, and "
                    "dummy-calls"),
                "dimensions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "system",
                    "endpoint": "pumpwood",
                    "route_type": "aux"},
                "icon": "",
                "extra_info": {}
            }, {
                #########
                # Admin #
                # It is possible to serve Pumpwood Admin adding a custom route
                # to pumpwood auth service.
                "route_url": "/admin/pumpwood-auth-app/gui/",
                "route_name": "admin--pumpwood-auth-app",
                "route_type": "admin",
                "description": "Pumpwood Auth Admin",
                "notes": (
                    "Admin for pumpwood-auth-app microservice."),
                "dimensions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "gui",
                    "route_type": "admin"},
                "icon": "",
                "extra_info": {}
            }, {
                #############
                # MEDIA_URL #
                # Media URL can be added using a custom route to pumpwood-auth
                # service.
                "route_url": "/" + MEDIA_URL,
                "route_name": "media--pumpwood-auth-app",
                "route_type": "media",
                "description": "Pumpwood Auth Media Files",
                "notes": (
                    "Path to serve files using links."),
                "dimensions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "media"},
                "icon": "",
                "extra_info": {}
            }, {
                ##############
                # Other APPs #
                # Other APPs like jet, grappeli or custom admin flavors can
                # be added as custom routes to associate end-points to
                # pumpwood-auth-app services
                "route_url": "/jet/",
                "route_name": "pumpwood-auth-app--jet",
                "route_type": "gui",
                "description": "End-point for Jet Package urls",
                "notes": (
                    "Serve Jet urls."),
                "dimensions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "gui"},
                "icon": "",
                "extra_info": {}
            }],

            # viewsets parameters can be used to register default pumpwood
            # end-points for model_class. Fuction will extract information
            # from view associationg them with routes at service, routes
            # will be created with /rest/{model_class}/ as route.
            viewsets=[
                RestKongRoute, RestKongService, RestUser,
                RestMetabaseDashboard, RestMetabaseDashboardParameter,
                RestPumpwoodI8nTranslation, RestPumpwoodPermissionPolicy,
                RestPumpwoodPermissionPolicyAction,
                RestPumpwoodPermissionGroup,
                RestPumpwoodPermissionUserGroupM2M,
                RestPumpwoodPermissionPolicyGroupM2M,
                RestPumpwoodPermissionPolicyUserM2M])

        ######################
        # Add other services #
        # Some other microservice can be registred using pumpwood-auth,
        # although they are not served directly by pumpwood-auth. This can
        # help to register service and routes for microservice without
        # the need of customizing the docker imagens.
        # This is parciculary usefull to deploy static files NGINX end-point.
        # It is possible to use NGINX to serve Django static files for
        # production use and register the end-points using auth microservice.
        register_auth_kong_objects(
            service_url=auth_static_service,
            service_name="static-files",
            healthcheck_route=None,
            service_description="Static Files",
            service_notes=(
                "Static files"),
            service_dimensions={
                "microservice": "pumpwood",
                "type": "static"},
            service_icon=None,
            service_extra_info={},
            routes=[{
                # Admin static files
                "route_url": "/static/",
                "route_name": "static",
                "route_type": "static",
                "description": "Static Files Routes",
                "notes": (
                    "Static files for all pumpwood"),
                "dimensions": {
                    "microservice": "pumpwood",
                    "service_type": "core",
                    "route_type": "static"},
                "icon": "",
                "extra_info": {}
            }])

        swagger_service_url = os.environ.get("SWAGGER_SERVICE_URL")
        if metabase_secret_key is not None:
            register_auth_kong_objects(
                service_url=swagger_service_url,
                service_name="swagger",
                healthcheck_route=None,
                service_description="Swagger OpenAPI",
                service_notes=(
                    "Front-end interface to test Pumpwood APIs"),
                service_dimensions={
                    "microservice": "swagger",
                    "type": "gui",
                    "function": "testing"},
                service_icon=None,
                service_extra_info={},
                routes=[{
                    # Admin static files
                    "route_url": "/swagger",
                    "route_name": "swagger--app",
                    "route_type": "gui",
                    "strip_path": False,
                    "description": "Swagger OpenAPI",
                    "notes": (
                        "Front-end interface to test Pumpwood APIs"),
                    "dimensions": {
                        "microservice": "swagger",
                        "service_type": "gui",
                        "route_type": "testing"},
                    "icon": "",
                    "extra_info": {}
                }])
```
"""
