"""Adjust Knox Authentication to use token and cache values."""
import os
from loguru import logger
from knox.auth import TokenAuthentication
from knox.settings import knox_settings
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework.authentication import get_authorization_header
from pumpwood_communication.cache import default_cache


PUMPWOOD__AUTH__TOKEN_CACHE_EXPIRE = int(os.getenv(
    'PUMPWOOD__AUTH__TOKEN_CACHE_EXPIRE', 30))
"""Time to set expire at token cache."""


class PumpwoodAuthentication(TokenAuthentication):
    """Pumpwood Authentication.

    It will cache authentication locally to reduce querys to database and
    also check cookies for `PumpwoodAuthorization` token.
    """

    def authenticate(self, request):
        """Authenticate request using header or cookie and cache results."""
        auth = get_authorization_header(request).split()
        prefix = knox_settings.AUTH_HEADER_PREFIX.encode()

        token = None
        if len(auth) != 0:
            # Check if token was passed as header at the request
            if auth[0].lower() != prefix.lower():
                # Authorization header is possibly for another backend
                return None
            if len(auth) == 1:
                msg = _(
                    'Invalid token header. No credentials provided.')
                raise exceptions.AuthenticationFailed(msg)
            elif len(auth) > 2:
                msg = _(
                    'Invalid token header. ' +
                    'Token string should not contain spaces.')
                raise exceptions.AuthenticationFailed(msg)
            else:
                token = auth[1]
        else:
            # Check if token was passed as a cookie at the request
            # Encode token to bytes for compatibility with header behavior
            cookie_token = request.COOKIES.get('PumpwoodAuthorization')
            if cookie_token is not None:
                token = cookie_token.encode("utf-8")

        # If authentication headers were not found, return None
        # as defaulf behavior of TokenAuthentication view.
        if token is None:
            return None

        # Try to retrieve user authentication from cache to reduce database
        # calls
        hash_dict = {
            'context': 'authentication_token',
            'token': token.decode("utf-8")}
        cache_data = default_cache.get(hash_dict=hash_dict)
        if cache_data is not None:
            user = cache_data['user']
            auth_token = cache_data['auth_token']
            msg = "get token from cache user[{user_id}]"\
                .format(user_id=user.id)
            logger.info(msg)
            return (cache_data['user'], cache_data['auth_token'])

        # If not possible, autheticate with the credentials and set
        # returned values for next calls cache
        user, auth_token = self.authenticate_credentials(token)
        default_cache.set(
            hash_dict=hash_dict,
            value={'user': user, 'auth_token': auth_token},
            expire=PUMPWOOD__AUTH__TOKEN_CACHE_EXPIRE)
        return (user, auth_token)
