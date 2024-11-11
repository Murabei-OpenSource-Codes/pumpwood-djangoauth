"""Views for authentication and user end-point."""
import os
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.signals import user_logged_in
from django.contrib.auth import login
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from pumpwood_communication import exceptions
from pumpwood_djangoauth.registration.models import (
    PumpwoodMFAMethod, PumpwoodMFAToken, PumpwoodMFACode,
    PumpwoodMFARecoveryCode)
from pumpwood_djangoauth.registration.serializers import SerializerUser

# Knox Views
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView

# Loging API calls
from pumpwood_djangoauth.log.functions import log_api_request

# I8N
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation as t

# SSO classes
from pumpwood_djangoauth.registration.mfa_aux.views.sso.microsoft_entra import (
    MicrosoftEntraSSO)


def create_sso_client():
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
    #####################################################################
    # Validate if email is registred at aplication before make SSO call #
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

    mfa_method = user.mfa_method_set.filter(
        type='sso', is_enabled=True, is_validated=True).first()
    if mfa_method is None:
        msg = "User is not associated with SSO authentication"
        raise exceptions.PumpWoodUnauthorized(msg)
    ####################################################################

    new_mfa_token = PumpwoodMFAToken(user=user)
    new_mfa_token.save()

    sso_client = create_sso_client()
    authorization_url = sso_client.create_authorization_url(
        state=new_mfa_token.token)

    response = Response({
        'mfa_method_type': mfa_method.type,
        'mfa_method_result': {
            'authorization_url': authorization_url['authorization_url']},
        'expiry': new_mfa_token.expire_at,
        'mfa_token': new_mfa_token.token,
        'user': None,
        "ingress-call": is_ingress_request})
    response.set_cookie(
        'PumpwoodMFAToken', new_mfa_token.token,
        expires=new_mfa_token.expire_at,
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE)
    response.set_cookie(
        'PumpwoodMFATokenExpiry', new_mfa_token.expire_at,
        expires=new_mfa_token.expire_at,
        httponly=settings.SESSION_COOKIE_HTTPONLY,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE)
    return response


class SSOLoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny, )

    def post(self, request, format=None):
        msg = (
            "SSO Login must be done using get request using authentication "
            "redirect url")
        raise exceptions.PumpWoodForbidden(msg)

    def get(self, request):
        """Login user with MFA Token and MFA Code."""
        is_ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')

        ###############################################
        # Use state parameter to prevent CSRF attacks #
        mfa_token = request.GET.get('state')
        if mfa_token is None:
            msg = (
                "SSO state parameter is not set, check authorization "
                "URL construction")
            raise exceptions.PumpWoodUnauthorized(msg)

        try:
            mfa_object = PumpwoodMFAToken.objects.get(token=mfa_token)
        except Exception:
            msg = 'MFA Token was not found'
            raise exceptions.PumpWoodUnauthorized(
                msg, payload={"error": "mfa_token_not_found"})

        now_time = timezone.now()
        if mfa_object.expire_at <= now_time:
            msg = 'MFA Token has expired, log in again'
            mfa_object.delete()
            raise exceptions.PumpWoodUnauthorized(
                msg, payload={"error": "mfa_token_expired"})

        ##############################################################
        # Use SSO to fetch information from user and check if database
        # information
        sso_client = create_sso_client()
        sso_user_info = sso_client.fetch_token(
            authorization_response_url=request.get_full_path())
        access_token_data = sso_user_info["access_token"]

        # Check if user has an SSO authentication associated with him/her
        user = mfa_object.user
        user_mfa_method = user.mfa_method_set.filter(type='sso').first()
        if user_mfa_method is None:
            msg = "User [{username}] is not associated with SSO authentication"
            raise exceptions.PumpWoodUnauthorized(
                msg, payload={'username': user.username})

        user_email = user.email
        user_upn = user_mfa_method.extra_info.get("upn")
        access_token_email = access_token_data.get("email")
        access_token_upn = access_token_data.get("upn")

        # If extra_info is not set for MFA method, try to use user email
        # to validate SSO if 'email' key is avaiable at access_token
        user_id_match = False
        if access_token_email is not None and user_upn is None:
            user_id_match = access_token_email == user_email

        # If MFA extra_info.upn is not None try to match the upn from
        # access token upn data
        elif user_upn is not None and access_token_upn is not None:
            user_id_match = user_upn == access_token_upn

        # If it was not possible to validate user identification according
        # to any of the extra_info data or user email, then raise an error
        # indicating the keys that were returned by access key token
        # and user associated information
        if not user_id_match:
            msg = (
                "It was not possible to verify user id matching " +
                "information from Pumpwood MFA Method and SSO access token " +
                "data.\n" +
                "- access token upn: [{access_token_upn}]\n" +
                "- access token email: [{access_token_email}]\n" +
                "- user upn: [{user_upn}]\n" +
                "- user email: [{user_email}]")
            raise exceptions.PumpWoodUnauthorized(
                msg, payload={
                    "access_token_upn": access_token_upn,
                    "access_token_email": access_token_email,
                    "user_upn": user_upn,
                    "user_email": user_email})

        # Ok it seem legit... Login user from SSO call
        login(request, user)

        ###################################################
        # Copy and past from post request at Knox package #
        token_limit_per_user = self.get_token_limit_per_user()
        if token_limit_per_user is not None:
            now = timezone.now()
            token = request.user.auth_token_set.filter(expiry__gt=now)
            if token.count() >= token_limit_per_user:
                msg = "Maximum amount of tokens allowed per user exceeded."
                return Response(
                    {"error": msg},
                    status=status.HTTP_403_FORBIDDEN)

        token_ttl = self.get_token_ttl()
        instance, token = AuthToken.objects.create(request.user, token_ttl)
        user_logged_in.send(
            sender=request.user.__class__,
            request=request, user=request.user)
        data = self.get_post_response_data(request, token, instance)

        response = Response({
            'expiry': data['expiry'], 'token': data['token'],
            'user': SerializerUser(request.user, many=False).data,
            "ingress-call": is_ingress_request})
        response.set_cookie(
            'PumpwoodAuthorization', data['token'],
            expires=data['expiry'],
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE)
        response.set_cookie(
            'PumpwoodAuthorizationExpiry', data['expiry'],
            expires=data['expiry'],
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE)
        return response
