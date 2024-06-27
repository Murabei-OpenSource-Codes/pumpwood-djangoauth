"""View for MFA using codes like SMS, email, etc..."""
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import login
from pumpwood_communication import exceptions
from pumpwood_djangoauth.registration.models import (
    PumpwoodMFAMethod, PumpwoodMFAToken, PumpwoodMFACode,
    PumpwoodMFARecoveryCode)
from pumpwood_djangoauth.registration.serializers import SerializerUser
from pumpwood_djangoauth.registration.views import validate_mfa_token

# Knox Views
from knox.views import LoginView as KnoxLoginView

# Loging API calls
from pumpwood_djangoauth.log.functions import log_api_request

# I8N
from pumpwood_djangoauth.i8n.models import PumpwoodI8nTranslation as t


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
    # Validate MFA token
    mfa_token_obj = validate_mfa_token(request)

    #############################################################
    # Fetch MFA method, used argument pk, but also filter by user
    # to not let user spoffing
    mfa_method = PumpwoodMFAMethod.objects.filter(
        user=mfa_token_obj.user, pk=pk).first()
    if mfa_method is None:
        msg = (
            'MFA code with pk[{pk}] does not exists or is not '
            'associated with current user').format(pk=pk)
        raise exceptions.PumpWoodObjectDoesNotExist(msg)

    # Run MFA method
    method_results = mfa_method.run_method(
        mfa_token=mfa_token_obj.token)
    is_ingress_request = request.headers.get(
        "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')

    return Response({
        'mfa_method_type': mfa_method.type,
        'mfa_method_result': method_results,
        'expiry': mfa_token_obj.expire_at,
        'mfa_token': mfa_token_obj.token,
        'user': None,
        "ingress-call": is_ingress_request})


class MFALoginView(KnoxLoginView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        """Login user with MFA Token and MFA Code."""
        request_data = request.data
        if "mfa_code" not in request_data.keys():
            msg = "Missing 'code' on resquest data"
            raise exceptions.PumpWoodWrongParameters(
                message=msg, payload={"mfa_code": ['missing']})

        # Validate MFA token
        mfa_token_obj = validate_mfa_token(request)
        is_ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')

        mfa_code = PumpwoodMFACode.objects.filter(
            token=mfa_token_obj, code=request_data["mfa_code"]).first()
        if mfa_code is None:
            msg = 'MFA code incorrect'
            raise exceptions.PumpWoodUnauthorized(
                message=msg, payload={"error": "mfa_code_not_found"})

        user = mfa_token_obj.user
        login(request, user)

        resp = super(MFALoginView, self).post(request, format=None).data
        response = Response({
            'expiry': resp['expiry'], 'token': resp['token'],
            'user': SerializerUser(request.user, many=False).data,
            "ingress-call": is_ingress_request})
        response.set_cookie(
            'PumpwoodAuthorization', resp['token'],
            httponly=True, samesite='Strict', expires=resp['expiry'],
            secure=True)
        response.set_cookie(
            'PumpwoodAuthorizationExpiry', resp['expiry'],
            httponly=True, samesite='Strict', expires=resp['expiry'],
            secure=True)
        return response
