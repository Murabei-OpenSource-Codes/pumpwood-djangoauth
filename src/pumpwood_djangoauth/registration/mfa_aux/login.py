"""Codes to help create MFA workflow."""
from django.conf import settings
from rest_framework.response import Response
from pumpwood_djangoauth.log.functions import log_api_request


class MFALoginResponse:
    """Class to help execute the logic of the MFA Login."""

    @classmethod
    def run(cls, priority_mfa, user: object,
            is_ingress_request: bool, full_path: str) -> Response:
        """Run the workflow to generate a MFA token and redirect user."""
        from pumpwood_djangoauth.registration.models import (
            PumpwoodMFAToken)
        new_mfa_token = PumpwoodMFAToken(user=user)
        new_mfa_token.save()
        method_result = priority_mfa.run_method(
            mfa_token=new_mfa_token.token)

        response = Response({
            'mfa_method_type': priority_mfa.type,
            'mfa_method_result': method_result,
            'expiry': new_mfa_token.expire_at,
            'mfa_token': new_mfa_token.token,
            'user': None,
            "ingress-call": is_ingress_request})
        response.set_cookie(
            'PumpwoodMFAToken', new_mfa_token.token,
            httponly=settings.SESSION_COOKIE_HTTPONLY,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE)
        response.set_cookie(
            'PumpwoodMFATokenExpiry', new_mfa_token.expire_at,
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
            payload='Password + MFA login')
        return response
