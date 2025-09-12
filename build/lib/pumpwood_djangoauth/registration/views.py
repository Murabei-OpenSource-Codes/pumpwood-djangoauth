"""Views for authentication and user end-point."""
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from pumpwood_communication import exceptions
from pumpwood_djangoviews.views import PumpWoodRestService

# Aux imports
from pumpwood_djangoauth.config import storage_object, microservice
from pumpwood_djangoauth.permissions import PumpwoodIsAuthenticated
from pumpwood_djangoauth.registration.mfa_aux import MFALoginResponse
from pumpwood_communication.exceptions import PumpWoodUnauthorized

# Models and serializers
from pumpwood_djangoauth.registration.models import (
    PumpwoodMFAToken, UserProfile)
from pumpwood_djangoauth.registration.serializers import SerializerUser

# Knox Views
from knox.views import LoginView as KnoxLoginView

# Loging API calls
from pumpwood_djangoauth.log.functions import log_api_request

# I8N
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation as t # NOQA


class LoginView(KnoxLoginView):
    """Login view that super KnoxLoginView."""

    # login view extending KnoxLoginView
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        """Login user using its password and username.

        Check if header have indication that the request came from "outside"
        """
        is_ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')
        full_path = request.path.strip("/")
        request_data = request.data

        # Validating Request
        validate_keys = set(request_data.keys())
        if validate_keys != {'username', 'password'}:
            msg = (
                "Login payload must have just username and password:\n"
                "espected: ['username', 'password']"
                "\npayload:{validate_keys}")
            log_api_request(
                user_id=None,
                permission_check='failed',
                request_method='post', path=full_path,
                model_class='registration',
                end_point='login',
                first_arg='',
                second_arg='',
                ingress_request=is_ingress_request,
                payload='Login payload must have just username and password')
            raise exceptions.PumpWoodWrongParameters(
                message=msg, payload={'validate_keys': validate_keys})
        if not request_data["password"]:
            msg = "Login password is empty"
            log_api_request(
                user_id=None,
                permission_check='failed',
                request_method='post', path=full_path,
                model_class='registration',
                end_point='login',
                first_arg='',
                second_arg='',
                ingress_request=is_ingress_request,
                payload=msg)
            raise exceptions.PumpWoodWrongParameters(
                message=msg)
        if not request_data["username"]:
            msg = "Login username is empty"
            log_api_request(
                user_id=None,
                permission_check='failed',
                request_method='post', path=full_path,
                model_class='registration',
                end_point='login',
                first_arg='',
                second_arg='',
                ingress_request=is_ingress_request,
                payload=msg)
            raise exceptions.PumpWoodWrongParameters(
                message=msg)

        # Autenticatng user
        user = authenticate(
            username=request_data["username"],
            password=request_data["password"])

        # If not possible to authenticate
        if user is None:
            msg = ("Username/Password incorrect")
            log_api_request(
                user_id=None,
                permission_check='ok',
                request_method='post', path=full_path,
                model_class='registration', end_point='login',
                first_arg=request_data["username"], second_arg='',
                ingress_request=is_ingress_request,
                payload=msg)
            raise exceptions.PumpWoodUnauthorized(
                message=msg, payload={"error": "incorrect_login"})

        # Check if user is is_service_user and for MFA
        is_service_user = user.user_profile.is_service_user
        priority_mfa = user.mfa_method_set.filter(
            is_enabled=True, is_validated=True).\
            order_by('priority').first()

        # If user is not a service and a MFA associated it will get a
        # MFA token, not the authentication token, this will be
        # used to msg MFAs that has authorization as first step
        if (priority_mfa is not None) and (not is_service_user):
            return MFALoginResponse.run(
                priority_mfa=priority_mfa, user=user,
                is_ingress_request=is_ingress_request,
                full_path=full_path)

        # Users without priority_mfa will receive authentication token
        # when loging with username/password
        else:
            # Service users should not log from outside of the cluster
            is_service_user = user.user_profile.is_service_user
            is_external_call = is_ingress_request == "EXTERNAL"
            if is_external_call and is_service_user:
                msg = ("EXTERNAL call using service users is not allowed")
                raise PumpWoodUnauthorized(message=msg)

            # Authenticate the request
            login(request, user)
            resp = super().post(request, format=None).data
            response = Response({
                'expiry': resp['expiry'], 'token': resp['token'],
                'user': SerializerUser(request.user, many=False).data,
                "ingress-call": is_ingress_request})
            response.set_cookie(
                'PumpwoodAuthorization', resp['token'],
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SESSION_COOKIE_SAMESITE,
                expires=resp['expiry'])
            response.set_cookie(
                'PumpwoodAuthorizationExpiry', resp['expiry'],
                expires=resp['expiry'],
                httponly=settings.SESSION_COOKIE_HTTPONLY,
                secure=settings.SESSION_COOKIE_SECURE,
                samesite=settings.SESSION_COOKIE_SAMESITE)
            log_api_request(
                user_id=user.id,
                permission_check='ok',
                request_method='post', path=full_path,
                model_class='registration', end_point='login',
                first_arg=user.username, second_arg='',
                ingress_request=is_ingress_request,
                payload='Password login')
            return response


# Fuction to validate MFA Token
def validate_mfa_token(request):
    """Validate MFA Token and return user if possible.

    Args:
        request:
            Django Rest request.

    Returns:
        Return user associated with MFA Token.
    """
    mfa_autorization = request.headers.get("X-PUMPWOOD-MFA-Autorization")
    try:
        mfa_object = PumpwoodMFAToken.objects.get(token=mfa_autorization)
    except Exception:
        msg = 'MFA Token was not found'
        raise exceptions.PumpWoodUnauthorized(
            msg, payload={"error": "mfa_token_not_found"})

    now_time = timezone.now()
    if mfa_object.expire_at <= now_time:
        msg = 'MFA Token has expired, loging again'
        mfa_object.delete()
        raise exceptions.PumpWoodUnauthorized(
            msg, payload={"error": "mfa_token_expired"})

    # Cleaning expired tokens
    PumpwoodMFAToken.objects.filter(expire_at__lte=now_time).delete()
    return mfa_object


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_user_mfa_methods(request):
    """Retrieve information about the authenticated user."""
    from pumpwood_djangoauth.registration.serializers import (
        SerializerPumpwoodMFAMethod)

    mfa_object = validate_mfa_token(request)
    mfa_method_set = mfa_object.user.mfa_method_set.all()
    mfa_method_set_data = SerializerPumpwoodMFAMethod(
        mfa_method_set, many=True).data
    return Response(mfa_method_set_data)


class CheckAuthentication(APIView):
    """API to validate login token and permission."""

    def get(self, request):
        """Authenticate call legacy."""
        permission = request.GET.get('permission', '')
        has_perm = True
        if permission:
            has_perm = request.user.has_perm(permission)

        # Do not log calls from outside of the cluster, calls from outside
        # of pumpwood cluster receive a X-PUMPWOOD-Ingress-Request=INGRESS
        # when passing trought NGINX termination.
        ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')

        # Do not log service users calls
        is_service_user = request.user.user_profile.is_service_user
        msg = (
            "# check registration [GET]: ingress_request[{ingress_request}]; "
            "is_service_user[{is_service_user}]").format(
                ingress_request=ingress_request,
                is_service_user=is_service_user)

        if not is_service_user and ingress_request != 'EXTERNAL':
            str_has_perm = 'ok' if has_perm else 'failed'
            log_api_request(
                user_id=request.user.id,
                permission_check=str_has_perm,
                request_method=None, path=None,
                model_class=None, end_point=None,
                first_arg=None, second_arg=None,
                payload=None)

        if not has_perm:
            msg = (
                "User does not have permission to exectute this action:\n"
                "expected permission: {permission}").format(
                    permission=permission)
            raise exceptions.PumpWoodUnauthorized(
                message=msg, payload={"permission": permission})
        return Response(True)

    def post(self, request):
        """Log API calls.

        New end-point that sets setting user_id and other information of the
        requested API.
        """
        request_data = request.data
        request_method = request_data.get("request_method")
        path = request_data.get("path", "").strip("/")

        # Geting modelo class of Pumpwood calls
        model_class = None
        path_split = path.split("rest/", maxsplit=2)
        if 1 < len(path_split):
            rest_url = path_split[1]
            model_class = rest_url.split("/", maxsplit=2)[0]

        end_point = request_data.get("end_point")
        first_arg = request_data.get("first_arg")
        second_arg = request_data.get("second_arg")
        payload = request_data.get("payload")
        ingress_request_check = request_data.get("ingress_request")

        # TODO: Create permission name from API call and check if user
        # can make this call.
        permission = ''
        has_perm = True
        if permission:
            has_perm = request.user.has_perm(permission)

        # Do not log calls from outside of the cluster, calls from outside
        # of pumpwood cluster receive a X-PUMPWOOD-Ingress-Request=INGRESS
        # when passing trought NGINX termination.
        ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')

        # Do not log service users calls
        is_service_user = request.user.user_profile.is_service_user
        msg = (
            "# check registration [POST]: ingress_request[{ingress_request}]; "
            "is_service_user[{is_service_user}]").format(
                ingress_request=ingress_request,
                is_service_user=is_service_user)
        print(msg)

        ############################################################
        # Do not log External permission check not to inflate logs #
        # with just check and not calls to other APIs
        # !! check if logic make sense...!!
        if not is_service_user and ingress_request != 'EXTERNAL':
            str_has_perm = 'ok' if has_perm else 'failed'
            log_api_request(
                user_id=request.user.id,
                permission_check=str_has_perm,
                request_method=request_method,
                path=path,
                model_class=model_class, end_point=end_point,
                first_arg=first_arg, second_arg=second_arg, payload=payload,
                ingress_request=ingress_request_check)

        # Raise error if user does not have permissions
        if not has_perm:
            msg = (
                "User does not have permission to exectute this action:\n"
                "expected permission: {permission}").format(
                    permission=permission)
            raise exceptions.PumpWoodUnauthorized(
                message=msg, payload={"permission": permission})
        return Response(True)


@api_view(['GET'])
@permission_classes([PumpwoodIsAuthenticated])
def retrieve_authenticated_user(request):
    """Retrieve information about the authenticated user."""
    self_user_data = SerializerUser(
        request.user, many=False, foreign_key_fields=True,
        related_fields=True, context={'request': request}).data
    return Response(self_user_data)


class RestUser(PumpWoodRestService):
    """End-point with information about Pumpwood users."""

    endpoint_description = "Users"
    notes = "End-point with user information"
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "user",
    }
    icon = None

    service_model = User
    serializer = SerializerUser
    storage_object = storage_object
    microservice = microservice

    #######
    # GUI #
    gui_retrieve_fieldset = [{
            "name": "main",
            "fields": [
                'username', 'first_name', 'last_name'
                'is_active', 'email', 'dimensions', 'last_login']
        }, {
            "name": "Admin permissions",
            "fields": [
                'is_service_user', 'is_superuser', 'is_staff',
                'all_permissions', 'group_permissions'
            ]
        }, {
            "name": "API permissions",
            "fields": [
                'api_permission_set',
            ]
        }, {
            "name": "extra_fields",
            "fields": ['extra_fields']
        }
    ]
    gui_readonly = ['last_login']
    gui_verbose_field = '{pk} | {username}'
    #######


class RestUserProfile(PumpWoodRestService):
    """End-point with information about Pumpwood users."""

    endpoint_description = "User Profile"
    notes = (
        "End-point user profile information and actions associated with "
        "api permission and other pumpwood user related")
    dimensions = {
        "microservice": "pumpwood-auth-app",
        "service_type": "core",
        "service": "auth",
        "type": "userprofile",
    }
    icon = None

    service_model = UserProfile
    serializer = SerializerUser
    storage_object = storage_object
    microservice = microservice

    #######
    # GUI #
    gui_retrieve_fieldset = None
    gui_readonly = []
    gui_verbose_field = '{pk}'
    #######
