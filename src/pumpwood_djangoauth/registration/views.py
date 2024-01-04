"""Views for authentication and user end-point."""
from django.utils import timezone
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from pumpwood_communication import exceptions
from pumpwood_djangoviews.views import PumpWoodRestService
from pumpwood_djangoauth.registration.models import (
    PumpwoodMFAMethod, PumpwoodMFAToken, PumpwoodMFACode,
    PumpwoodMFARecoveryCode)
from pumpwood_djangoauth.registration.serializers import SerializerUser

# Knox Views
from knox.views import LoginView as KnoxLoginView

# Loging API calls
from pumpwood_djangoauth.log.functions import log_api_request


class LoginView(KnoxLoginView):
    # login view extending KnoxLoginView
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        """
        Login user using its password and username.

        Check if header have indication that the request came from "outside"
        """
        is_ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')
        request_data = request.data

        # Validating Request
        validate_keys = set(request_data.keys())
        if validate_keys != {'username', 'password'}:
            msg = (
                "Login payload must have just username and password:\n"
                "espected: ['username', 'password']"
                "\npayload:{validate_keys}").format(
                    validate_keys=validate_keys)
            raise exceptions.PumpWoodWrongParameters(
                message=msg)
        if not request_data["password"]:
            msg = ("Login password is empty")
            raise exceptions.PumpWoodWrongParameters(
                message=msg)
        if not request_data["username"]:
            msg = ("Login username is empty")
            raise exceptions.PumpWoodWrongParameters(
                message=msg)

        # Autenticatng user
        user = authenticate(
            username=request_data["username"],
            password=request_data["password"])
        # Loging authentication attempts
        user_id = None
        if user is not None:
            user_id = user.id
        log_api_request(
            user_id=user_id,
            permission_check='failed' if user_id is None else 'ok',
            request_method='post', path=request.get_full_path(),
            model_class='registration', end_point='login',
            first_arg=request_data["username"],
            second_arg='',
            ingress_request=is_ingress_request,
            payload=None)

        if user is not None:
            is_service_user = user.user_profile.is_service_user
            priority_mfa = user.mfa_method_set.order_by('priority').first()

            ###############################################################
            # If user is not a service and a MFA associated it will get a
            # MFA token, not the authentication token
            if (priority_mfa is not None) and (not is_service_user):
                # Create a token to validate MFA login and creation
                new_mfa_token = PumpwoodMFAToken(user=user)
                new_mfa_token.save()

                # Create MFA token using primary mfa
                mfa_code = PumpwoodMFACode(
                    token=new_mfa_token, mfa_method=priority_mfa)
                mfa_code.save()

                return Response({
                    'expiry': new_mfa_token.expire_at,
                    'mfa_token': new_mfa_token.token,
                    'user': None,
                    "ingress-call": is_ingress_request})

            # Users without priority_mfa will receive authentication token
            # when loging with username/password
            else:
                login(request, user)
                is_service_user = user.user_profile.is_service_user
                is_external_call = is_ingress_request == "EXTERNAL"
                if is_external_call and is_service_user:
                    msg = ("EXTERNAL call using serice users is not allowed")
                    raise exceptions.PumpWoodUnauthorized(message=msg)

                resp = super(LoginView, self).post(request, format=None).data
                return Response({
                    'expiry': resp['expiry'], 'token': resp['token'],
                    'user': SerializerUser(request.user, many=False).data,
                    "ingress-call": is_ingress_request})
        else:
            msg = ("Username/Password incorrect")
            raise exceptions.PumpWoodUnauthorized(
                message=msg, payload={"error": "incorrect_login"})


# Fuction to validate MFA Token
def validate_mfa_token(request):
    """
    Validate MFA Token and return user if possible.

    Args:
        request: Django Rest request.
    Return [User]:
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


#########################################################################
# TODO: Terminar o end-point que faz a criação de um novo código de MFA #
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def create_new_mfa_code(request, pk=None):
    """
    Create a new MFA code.

    Args:
        request: Django Rest request.
    Return [bool]:
        Return True if code sent to MFA.
    """
    mfa_token_obj = validate_mfa_token(request)
    mfa_code = PumpwoodMFACode(
        token=new_mfa_token, mfa_method=mfa_token_obj)
    mfa_code.save()

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
        print(msg)
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
        """
        Log API calls.

        New end-point that sets setting user_id and other information of the
        requested API.
        """
        request_data = request.data
        request_method = request_data.get("request_method")
        path = request_data.get("path")

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
                path=path, model_class=model_class, end_point=end_point,
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
def retrieve_authenticated_user(request):
    """Retrieve information about the authenticated user."""
    return Response(
        SerializerUser(request.user, many=False).data)


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
    list_fields = [
        "pk", "model_class", 'username', 'email', 'first_name',
        'last_name', 'last_login', 'date_joined', 'is_active', 'is_staff',
        'is_superuser', 'is_service_user', 'dimensions', 'extra_fields',
        'all_permissions', 'group_permissions', 'user_profile']
    foreign_keys = {}
