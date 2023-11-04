"""Views for authentication and user end-point."""
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.authtoken.models import Token
from pumpwood_communication import exceptions
from pumpwood_djangoviews.views import PumpWoodRestService
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from pumpwood_djangoauth.registration.serializers import SerializerUser

# Knox Views
from knox.views import LoginView as KnoxLoginView


class LoginView(KnoxLoginView):
    # login view extending KnoxLoginView
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        """
        Login user using its password and username.

        Check if header have indication that the request came from "outside"
        """
        is_ingress_request = request.headers.get(
            "Ingress-Request", 'not-ingress')
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
        if user is not None:
            login(request, user)
            resp = super(LoginView, self).post(request, format=None).data
            return Response({
                'expiry': resp['expiry'],
                'token': resp['token'],
                'user': SerializerUser(request.user, many=False).data,
                "ingress-call": is_ingress_request})
        else:
            msg = ("Username/Password incorrect")
            raise exceptions.PumpWoodUnauthorized(
                message=msg)


@api_view(['GET'])
def check_logged(request):
    """Check if user is logged and have the permission."""
    permission = request.GET.get('permission', '')
    if permission:
        has_perm = request.user.has_perm(permission)
        if not has_perm:
            msg = (
                "User does not have permission to exectute this action:\n"
                "expected permission: {permission}").format(
                    permission=permission)
            raise exceptions.PumpWoodUnauthorized(
                message=msg, payload={
                    "permission": permission})
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
        'is_superuser', 'is_microservice', 'dimensions', 'extra_fields',
        'all_permissions', 'group_permissions', 'user_profile']
    foreign_keys = {}
