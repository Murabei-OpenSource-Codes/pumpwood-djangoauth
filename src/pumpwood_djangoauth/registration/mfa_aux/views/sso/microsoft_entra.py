"""Make calls to perform SSO using MicrosoftEntra."""
import os
import urllib.parse
import jwt
from pumpwood_communication import exceptions
from requests_oauthlib import OAuth2Session


class MicrosoftEntraSSO:
    """Class to help performing Microsoft Entra SSO."""

    SCOPE = ['openid', 'profile', 'email']

    def __init__(self, ):
        """."""
        PUMPWOOD__SSO__REDIRECT_URL = os.getenv(
            "PUMPWOOD__SSO__REDIRECT_URL")
        PUMPWOOD__SSO__AUTHORIZATION_URL = os.getenv(
            "PUMPWOOD__SSO__AUTHORIZATION_URL")
        PUMPWOOD__SSO__TOKEN_URL = os.getenv(
            "PUMPWOOD__SSO__TOKEN_URL")
        PUMPWOOD__SSO__CLIENT_ID = os.getenv(
            "PUMPWOOD__SSO__CLIENT_ID")
        PUMPWOOD__SSO__SECRET = os.getenv(
            "PUMPWOOD__SSO__SECRET")

        is_BASE_REDIRECT_URL_set = \
            (PUMPWOOD__SSO__REDIRECT_URL is None)
        is_AUTHORIZATION_URL_set = \
            (PUMPWOOD__SSO__AUTHORIZATION_URL is None)
        is_TOKEN_URL_set = \
            (PUMPWOOD__SSO__TOKEN_URL is None)
        is_CLIENT_ID_set = \
            (PUMPWOOD__SSO__CLIENT_ID is None)
        is_SECRET_set = \
            (PUMPWOOD__SSO__SECRET is None)
        check_variables = (
            is_BASE_REDIRECT_URL_set or is_AUTHORIZATION_URL_set or
            is_TOKEN_URL_set or is_CLIENT_ID_set or is_SECRET_set)
        if check_variables:
            msg = (
                "Enviroment variables PUMPWOOD__SSO__PROVIDER, "
                "PUMPWOOD__SSO__AUTHORIZATION_URL, PUMPWOOD__SSO__TOKEN_URL, "
                "PUMPWOOD__SSO__CLIENT_ID, "
                "PUMPWOOD__SSO__SECRET must be set to use "
                "Microsoft Entra as SSO. Variables status:\n"
                "- is PUMPWOOD__SSO__REDIRECT_URL set: "
                "{is_BASE_REDIRECT_URL_set}\n"
                "- is PUMPWOOD__SSO__AUTHORIZATION_URL set: "
                "{is_AUTHORIZATION_URL_set}\n"
                "- is PUMPWOOD__SSO__TOKEN_URL set: {is_TOKEN_URL_set}\n"
                "- is PUMPWOOD__SSO__CLIENT_ID set: {is_CLIENT_ID_set}\n"
                "- is PUMPWOOD__SSO__SECRET set: {is_SECRET_set}")
            raise exceptions.PumpWoodForbidden(
                msg, payload={
                    "is_BASE_REDIRECT_URL_set": is_BASE_REDIRECT_URL_set,
                    "is_AUTHORIZATION_URL_set": is_AUTHORIZATION_URL_set,
                    "is_TOKEN_URL_set": is_TOKEN_URL_set,
                    "is_CLIENT_ID_set": is_CLIENT_ID_set,
                    "is_SECRET_set": is_SECRET_set})

        # Create callback url
        self._redirect_uri = PUMPWOOD__SSO__REDIRECT_URL
        self.PUMPWOOD__SSO__AUTHORIZATION_URL = \
            PUMPWOOD__SSO__AUTHORIZATION_URL
        self.PUMPWOOD__SSO__TOKEN_URL = \
            PUMPWOOD__SSO__TOKEN_URL
        self.PUMPWOOD__SSO__CLIENT_ID = \
            PUMPWOOD__SSO__CLIENT_ID
        self.PUMPWOOD__SSO__SECRET = \
            PUMPWOOD__SSO__SECRET

    def create_authorization_url(self, state: str):
        """
        Create authentication URL for Microsoft Entra SSO.

        Args:
            state [str]: Random string used to counter CSRF attacks.
        Kwargs:
            No Kwargs.
        Return [dict]:
            Dictionary with generated authorization_url and state parameter.
        """
        oauth = OAuth2Session(
            self.PUMPWOOD__SSO__CLIENT_ID,
            redirect_uri=self._redirect_uri,
            scope=self.SCOPE)
        authorization_url, state = oauth.authorization_url(
            self.PUMPWOOD__SSO__AUTHORIZATION_URL, state=state)
        return {
            "authorization_url": authorization_url,
            "state": state}

    def fetch_token(self, authorization_response_url: str):
        """
        Fetch authorization token and user information.

        Args:
            authorization_response_url [str]: Autorization response url
                passed after redirect of SSO authentication.
        Kwargs:

        """
        ##############################################################
        # Set OAUTHLIB_INSECURE_TRANSPORT it crashs with sub-domains #
        os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'
        ##############################################################

        oauth = OAuth2Session(
            self.PUMPWOOD__SSO__CLIENT_ID,
            redirect_uri=self._redirect_uri,
            scope=self.SCOPE)
        token = oauth.fetch_token(
            self.PUMPWOOD__SSO__TOKEN_URL,
            authorization_response=authorization_response_url,
            client_secret=self.PUMPWOOD__SSO__SECRET)
        decoded_token = jwt.decode(
            token['id_token'], options={"verify_signature": False})
        with_email = (
            'email' in decoded_token.keys())
        with_preferred_username = (
            'preferred_username' in decoded_token.keys())

        if with_email:
            return {"email": decoded_token['email']}
        elif with_preferred_username:
            return {"email": decoded_token['preferred_username']}
        else:
            msg = (
                'Entra Token does not contain user email, ' +
                'it is not possible to login')
            raise exceptions.PumpWoodUnauthorized(msg)
