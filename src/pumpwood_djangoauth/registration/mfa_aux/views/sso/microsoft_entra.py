"""Make calls to perform SSO using MicrosoftEntra."""
import os
import jwt
import json
from pumpwood_communication import exceptions
from requests_oauthlib import OAuth2Session
from pumpwood_djangoauth.config import (
    PUMPWOOD__SSO__REDIRECT_URL, PUMPWOOD__SSO__AUTHORIZATION_URL,
    PUMPWOOD__SSO__TOKEN_URL, PUMPWOOD__SSO__CLIENT_ID, PUMPWOOD__SSO__SECRET,
    PUMPWOOD__SSO__SCOPE, SSO_PROXY_CONFIG)

# If OAUTHLIB_RELAX_TOKEN_SCOPE is not explicity set, than set to 1
# this will relax the SCOPE validation from OAuth package.
# It seems that entra might change the SCOPE giving more access than
# requested
if 'OAUTHLIB_RELAX_TOKEN_SCOPE' not in os.environ:
    os.environ['OAUTHLIB_RELAX_TOKEN_SCOPE'] = '1' # NOQA


# Set OAUTHLIB_INSECURE_TRANSPORT it crashs with sub-domains #
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class MicrosoftEntraSSO:
    """Class to help performing Microsoft Entra SSO."""

    def __init__(self, ):
        """."""
        pumpwood__sso__redirect_url = PUMPWOOD__SSO__REDIRECT_URL
        pumpwood__sso__authorization_url = PUMPWOOD__SSO__AUTHORIZATION_URL
        pumpwood__sso__token_url = PUMPWOOD__SSO__TOKEN_URL
        pumpwood__sso__client_id = PUMPWOOD__SSO__CLIENT_ID
        pumpwood__sso__secret = PUMPWOOD__SSO__SECRET
        # In some environment env variable it is set as an empty
        # string 'or' will treat both None and empty string values
        pumpwood__sso__scope = PUMPWOOD__SSO__SCOPE

        is_base_redirect_url_set = \
            (pumpwood__sso__redirect_url is None)
        is_authorization_url_set = \
            (pumpwood__sso__authorization_url is None)
        is_token_url_set = \
            (pumpwood__sso__token_url is None)
        is_client_id_set = \
            (pumpwood__sso__client_id is None)
        is_secret_set = \
            (pumpwood__sso__secret is None)

        check_variables = (
            is_base_redirect_url_set or is_authorization_url_set or
            is_token_url_set or is_client_id_set or is_secret_set)

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
                    "is_BASE_REDIRECT_URL_set": is_base_redirect_url_set,
                    "is_AUTHORIZATION_URL_set": is_authorization_url_set,
                    "is_TOKEN_URL_set": is_token_url_set,
                    "is_CLIENT_ID_set": is_client_id_set,
                    "is_SECRET_set": is_secret_set})

        # Create callback url
        self._redirect_uri = \
            pumpwood__sso__redirect_url
        self.PUMPWOOD__SSO__AUTHORIZATION_URL = \
            pumpwood__sso__authorization_url
        self.PUMPWOOD__SSO__TOKEN_URL = \
            pumpwood__sso__token_url
        self.PUMPWOOD__SSO__CLIENT_ID = \
            pumpwood__sso__client_id
        self.PUMPWOOD__SSO__SECRET = \
            pumpwood__sso__secret

        # Check for valid JSON input in PUMPWOOD__SSO__SCOPE
        try:
            self.PUMPWOOD__SSO__SCOPE = json.loads(pumpwood__sso__scope)
        except json.JSONDecodeError as e:
            raise exceptions.PumpWoodForbidden(
                "PUMPWOOD__SSO__SCOPE environment variable "
                "is not a valid JSON: {}".format(pumpwood__sso__scope),
                payload={"error": str(e)})

        # Create the OAuth2Session object and set the proxy if defined
        self.oauth_session = OAuth2Session(
            self.PUMPWOOD__SSO__CLIENT_ID,
            redirect_uri=self._redirect_uri,
            scope=self.PUMPWOOD__SSO__SCOPE)
        if SSO_PROXY_CONFIG is not None:
            self.oauth_session.proxies.update(SSO_PROXY_CONFIG)

    def create_authorization_url(self, state: str):
        """Create authentication URL for Microsoft Entra SSO.

        Args:
            state (str):
                Random string used to counter CSRF attacks.

        Returns:
            Dictionary with generated authorization_url and state parameter.
        """
        authorization_url, state = self.oauth_session.authorization_url(
            self.PUMPWOOD__SSO__AUTHORIZATION_URL, state=state)
        return {
            "authorization_url": authorization_url,
            "state": state}

    def fetch_token(self, authorization_response_url: str):
        """Fetch authorization token and user information.

        Args:
            authorization_response_url (str):
                Autorization response url passed after redirect of SSO
                authentication.
        """
        token = self.oauth_session.fetch_token(
            self.PUMPWOOD__SSO__TOKEN_URL,
            authorization_response=authorization_response_url,
            client_secret=self.PUMPWOOD__SSO__SECRET)
        decoded_id_token = jwt.decode(
            token['id_token'], options={"verify_signature": False})
        decoded_access_token = jwt.decode(
            token['access_token'], options={"verify_signature": False})
        return {
            "id_token": decoded_id_token,
            "access_token": decoded_access_token, }
