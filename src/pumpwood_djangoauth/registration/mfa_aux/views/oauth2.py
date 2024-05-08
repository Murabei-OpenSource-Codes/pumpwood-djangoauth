"""Views for authentication and user end-point."""
import os
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

# Loging API calls
from pumpwood_djangoauth.log.functions import log_api_request

# I8N
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation as t

# SSO classes
from pumpwood_djangoauth.registration.mfa_aux.views.sso.microsoft_entra import(
    MicrosoftEntraSSO)


def __create_sso_client():
    PUMPWOOD__SSO__PROVIDER = os.getenv("PUMPWOOD__SSO__PROVIDER")
    if PUMPWOOD__SSO__PROVIDER is None:
        msg = (
            "PUMPWOOD__SSO__PROVIDER is not set. It is not possible to use "
            "SSO login.")
        raise exceptions.PumpWoodNotImplementedError(msg)

    if PUMPWOOD__SSO__PROVIDER == "microsoft-entra":
        return MicrosoftEntraSSO()
    else:
        msg = (
            "Single Sign-On provider [{sso_provider}] not "
            "implemented")
        raise exceptions.PumpWoodNotImplementedError(
            msg, payload={"sso_provider": PUMPWOOD__SSO__PROVIDER})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def oauth2_get_authorization_url(request):
    """
    Processs callback from Auth2.

    Args:
        email [str]: User e-mail to generate SSO log-in.
    Return [str]:
        .
    """
    ####################################################################
    # Validate if email is registred at aplication before make SSO call#
    is_ingress_request = request.headers.get(
        "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')
    request_data = request.data

    payload_keys = set(request_data.keys())
    if payload_keys != {'email', }:
        msg = (
            "SSO Login payload must have just email:\n"
            "espected: ['email']"
            "\npayload:{payload_keys}").format(
                payload_keys=payload_keys)
        raise exceptions.PumpWoodWrongParameters(
            message=msg, payload={'payload_keys': payload_keys})

    if not request_data["email"]:
        msg = ("Email is empty")
        raise exceptions.PumpWoodWrongParameters(message=msg)

    user = User.objects.filter(email=request_data["email"]).first()
    if user is None:
        msg = "Email not found"
        raise exceptions.PumpWoodUnauthorized(msg)

    mfa_method = user.mfa_method_set.filter(type='sso').first()
    if mfa_method is None:
        msg = "User is not associated with SSO authentication"
        raise exceptions.PumpWoodUnauthorized(msg)
    ####################################################################

    sso_client = __create_sso_client()
    authorization_url = sso_client.create_authorization_url()
    return Response({
        'mfa_method_type': mfa_method.type,
        'mfa_method_result': {
            'authorization_url': authorization_url['authorization_url']
        },
        'expiry': None,
        'mfa_token': None,
        'user': None,
        "ingress-call": is_ingress_request})


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def processs_oauth2_callback(request):
    """
    Processs callback from Auth2.

    Args:
        No args.
    Return [str]:
        .
    """
    sso_client = __create_sso_client()
    sso_user_info = sso_client.fetch_token(
        authorization_response_url=request.get_full_path())

    # Check if e-mail used to login is at database
    user = User.objects.filter(email=sso_user_info["email"]).first()
    if user is None:
        msg = "Email [{email}] used at SSO is not present at database"
        raise exceptions.PumpWoodUnauthorized(
            msg, payload={'email': sso_user_info["email"]})

    mfa_method = user.mfa_method_set.filter(type='sso').first()
    if mfa_method is None:
        msg = "Email [{email}] is not associated with SSO authentication"
        raise exceptions.PumpWoodUnauthorized(
            msg, payload={'email': sso_user_info["email"]})
    return Response({})


class SSOLoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def get(self, request):
        """Login user with MFA Token and MFA Code."""
        is_ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')

        sso_client = __create_sso_client()
        sso_user_info = sso_client.fetch_token(
            authorization_response_url=request.get_full_path())

        # Check if e-mail used to login is at database
        user = User.objects.filter(email=sso_user_info["email"]).first()
        if user is None:
            msg = "Email [{email}] used at SSO is not present at database"
            raise exceptions.PumpWoodUnauthorized(
                msg, payload={'email': sso_user_info["email"]})

        mfa_method = user.mfa_method_set.filter(type='sso').first()
        if mfa_method is None:
            msg = "Email [{email}] is not associated with SSO authentication"
            raise exceptions.PumpWoodUnauthorized(
                msg, payload={'email': sso_user_info["email"]})

        # Login user from SSO call
        login(request, user)
        resp = super().post(request, format=None).data
        return Response({
            'expiry': resp['expiry'], 'token': resp['token'],
            'user': SerializerUser(request.user, many=False).data,
            "ingress-call": is_ingress_request})
