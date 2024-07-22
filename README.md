# PumpWood Django Auth
Create basic Pumpwood end-points for authentication and service mesh using
Kong. It integrates with
<a href="https://github.com/Murabei-OpenSource-Codes/pumpwood-communication">
    pumpwood-communication

</a> and <a href="https://github.com/Murabei-OpenSource-Codes/pumpwood-djangoviews">
    pumpwood-djangoviews
</a>.

<p align="center" width="60%">
  <img src="static_doc/sitelogo-horizontal.png" /> <br>

  <a href="https://en.wikipedia.org/wiki/Cecropia">
    Pumpwood is a native brasilian tree
  </a> which has a symbiotic relation with ants (Murabei)
</p>

## Environment variables
Some environment variables are used to configuration features at the package:

### Kong integration (API_GATEWAY_URL)
To set the Kong Api host, use the environment variable `API_GATEWAY_URL`.
Calling system end-point without setting the variable may lead to errors.

### Pumpwood Microservice Integration
It is possible to use microservice objects to call other Pumpwood end-points,
or even make a self call in multi-process architecture (more than one
instance of the authentication application). For at it is necessary to set:

- `MICROSERVICE_NAME`: microservice object name, used for debug pourposes.
- `MICROSERVICE_URL`: Full path of the Pumpwood Api Gateway or Service Mesh.
- `MICROSERVICE_USERNAME`: Username to be used at login.
- `MICROSERVICE_PASSWORD`: Password to be used at login.

### Pumpwood Storage Integration
- `STORAGE_TYPE`: storage type to be used serving media files [google_bucket, aws_s3, azure_storage]
- `STORAGE_BUCKET_NAME`: Name of the bucket, blog or S3 to be used.
- `STORAGE_BASE_PATH`: Base path to be used when saving files with auth microservice.

#### Pumpwood Storage cloud configuration
Depending on the storage back-end, it must be provided credentials and other information.
- aws_s3
  -  `AWS_ACCESS_KEY_ID`: Access Key for the service user to access s3.
  - `AWS_SECRET_ACCESS_KEY`:  Secret Key for the service user to access s3.
- azure_storage
  - `AZURE_STORAGE_CONNECTION_STRING`: Storage connection string to access storage account.
- google_bucket
  - `GOOGLE_APPLICATION_CREDENTIALS`: Path for the google application credentials.

### Logging user activity
It is possible to log consumer activify using RabbitMQ and a cosumer process
this option is activated using `PUMPWOOD_AUTH_IS_RABBITMQ_LOG` parameter.
All call that has `X-PUMPWOOD-Ingress-Request` header (that may be set using
a NGINX termination container) and user that request is not a a service user
(`UserProfile.is_service_user == False`) will be sent to `auth__api_request_log`
RabbitMQ queue.
- `PUMPWOOD_AUTH_IS_RABBITMQ_LOG [TRUE, FALSE]`: Set if authentication logs
  should be sent to RabbitMQ (TRUE) or just printed on stdout (FALSE).
  If `PUMPWOOD_AUTH_IS_RABBITMQ_LOG` is `TRUE`, but RabbitMQ credentials are not
  set authentication logs will be sent to stdout anyway.

## Quick start
Crate basic models and end-points to integrate with pumpwood communication
and views. To incorporate in project add to `settings.py`.

```
INSTALLED_APPS = [
    # Django Pumpwood Auth Models
    'pumpwood_djangoauth.registration',
    'pumpwood_djangoauth.system',

    [...]
]
```

Add views to url.py:
```
urlpatterns = [
    [...],
    # Health check, it is important to set a health check end-point.
    url(r'^health-check/pumpwood-auth-app/',
        lambda r: JsonResponse(True, safe=False)),

    # Registration end-points
    url(r'^rest/', include('pumpwood_djangoauth.registration.urls')),
    url(r'^rest/', include('pumpwood_djangoauth.system.urls')),

    [...],
]
```

### Registering end-points
To register end-points it is possible to use register_auth_kong_objects.
It is possible to set using a dictionary or using pumpwood views.

```
from pumpwood_djangoauth.kong.create_routes import register_auth_kong_objects
from pumpwood_djangoauth.system.views import (
    RestKongRoute, RestKongService)
from pumpwood_djangoauth.registration.views import RestUser

# Pumpwood Views from models
from people.rest import (RestPeople, RestCats)

# Enviroment variable defining path to the service at the cluster
# (may be akubenetes service)
service_url = os.environ.get("SERVICE_URL")

# Register rest end-points and admin
register_auth_kong_objects(
    # Set description of the services that will receive the routes

    service_url=service_url,
    service_name="people-and-cats-main",
    healthcheck_route="/health-check/pumpwood-auth-app/",
    service_description="Main auth application",
    service_notes=(
        "Main app."),
    service_dimentions={
        "microservice": "pumpwood-auth-app",
        "type": "core",
        "function": "authentication"},
    service_icon=None,
    service_extra_info={},

    # These routes are necessary for auth
    routes=[{
        "route_url": "/rest/registration/",
        "route_name": "api--registration",
        "route_type": "aux",
        "description": "Registration",
        "notes": (
            "End-point for login, logout and other Authentication "
            "functions"),
        "dimentions": {
            "microservice": "pumpwood-auth-app",
            "service_type": "core",
            "function": "authentication",
            "endpoint": "registration",
            "route_type": "aux"},
        "icon": "",
        "extra_info": {}
    }, {

    # Some auxiliary end-points for Pumpwood
        "route_url": "/rest/pumpwood/",
        "route_name": "api--pumpwood",
        "route_type": "aux",
        "description": "Pumpwood System",
        "notes": (
            "System related end-points to list Kong routes, and "
            "dummy-calls"),
        "dimentions": {
            "microservice": "pumpwood-auth-app",
            "service_type": "core",
            "function": "system",
            "endpoint": "pumpwood",
            "route_type": "aux"},
        "icon": "",
        "extra_info": {}
    }, {

    # Add admin routes if necessary
        "route_url": "/admin/pumpwood-auth-app/",
        "route_name": "admin--pumpwood-auth-app",
        "route_type": "admin",
        "description": "Pumpwood Auth Admin",
        "notes": (
            "Admin for pumpwood-auth-app microservice."),
        "dimentions": {
            "microservice": "pumpwood-auth-app",
            "service_type": "core",
            "function": "gui",
            "route_type": "admin"},
        "icon": "",
        "extra_info": {}
    }, {

    # Add gui and other routes if necessary
        "route_url": "/gui/",
        "route_name": "gui--pumpwood-auth-app",
        "route_type": "gui",
        "description": (
            "Cats and people GUI"),
        "notes": (
            "GUI to access cats and people GUI."),
        "dimentions": {
            "microservice": "pumpwood-auth-app",
            "service_type": "core",
            "function": "gui",
            "route_type": "gui"},
        "icon": "",
        "extra_info": {}
    }],

    # Expose Pumpwood Rest Views end-points
    viewsets=[
        RestKongRoute, RestKongService, RestUser,
        RestPeople, RestCats])
```

### Login MFA
Enviroment variables:
- **PUMPWOOD__MFA__TOKEN_EXPIRATION_INTERVAL:** Set expiration interval of the
  MFA token sent to user, it is in seconds.
- **PUMPWOOD__MFA__APPLICATION_NAME:** Set application name to be used on
  MFA messages.

### Twilio SMS Message
To send SMS using Twilio back-end it is necessary to set these Environment
variables.
- **PUMPWOOD__MFA__TWILIO_ACCOUNT_SID:** Twilio Account SID.
- **PUMPWOOD__MFA__TWILIO_AUTH_TOKEN:** Twilio Auth Token.
