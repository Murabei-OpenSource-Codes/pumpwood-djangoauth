"""Logging Middlewares."""
import logging
from pumpwood_djangoauth.log.functions import log_api_request
from knox.auth import TokenAuthentication
from pumpwood_djangoauth.config import MEDIA_URL

request_logger = logging.getLogger(__name__)


def list_get_or_none(list_obj, i):
    """Get an element from a list or return None."""
    return list_obj[i] if i < len(list_obj) else None


class RequestLogMiddleware:
    """Request Logging Middleware for Pumpwood Calls."""

    knox_auth_token = None

    def __init__(self, get_response):
        """__init__."""
        self.get_response = get_response

    def __call__(self, request):
        """__call__."""
        content_type = request.content_type
        full_path = request.path.strip("/")
        splited_full_path = full_path.split("/")

        root_path = list_get_or_none(splited_full_path, 0)
        media_path = MEDIA_URL.strip("/")
        if content_type == "application/json":
            if root_path == 'rest':
                # Do not log login and check, end-points already do that
                not_check = 'rest/registration/check' not in full_path
                not_login = 'rest/registration/login' not in full_path
                if not_check and not_login:
                    self.log_rest_calls(request)

        elif full_path.startswith(media_path):
            self.log_media_calls(request)

        else:
            if (root_path == 'admin') and ('jsi18n' not in full_path):
                self.log_admin_calls(request)
        return self.get_response(request)

    def log_admin_calls(self, request):
        """Log admin calls on Pumpwood Backends."""
        if request.user is None:
            return None

        full_path = request.path.strip("/")
        splited_full_path = full_path.split("/")
        request_method = request.method.lower()
        model_class = list_get_or_none(splited_full_path, 5)
        end_point = list_get_or_none(splited_full_path, 7)
        first_arg = list_get_or_none(splited_full_path, 6)

        # Do not log payload with multipart
        payload = None
        is_multipart = request.content_type == "multipart/form-data"
        if request_method == 'post' and not is_multipart:
            payload = request.body[:300]

        log_api_request(
            user_id=request.user.id,
            permission_check='ok',
            model_class=model_class,
            request_method=request_method,
            path=full_path,
            end_point=end_point,
            first_arg=first_arg,
            second_arg=None,
            payload=payload)

    def log_media_calls(self, request):
        """Log Media calls using django views."""
        if request.user is None:
            return None

        full_path = request.path.strip("/")
        splited_full_path = full_path.split("/")
        request_method = request.method.lower()
        media_path = list_get_or_none(splited_full_path, 1)
        log_api_request(
            user_id=request.user.id,
            permission_check='ok',
            model_class=None,
            request_method=request_method,
            path=full_path,
            end_point="media",
            first_arg=media_path,
            second_arg=None,
            payload=None)

    def log_rest_calls(self, request):
        """Log rest calls on Pumpwood Backends."""
        if self.knox_auth_token is None:
            self.knox_auth_token = TokenAuthentication()

        # Get user from Django Knox token
        try:
            auth_resp = self.knox_auth_token.authenticate(request)
            ################################################################
            # Do not log anonymous calls, they will return unauthenticated #
            # they will return error
            if auth_resp is None:
                return None
            user, auth_token = auth_resp
        except Exception:
            return None

        ingress_request = request.headers.get(
            "X-PUMPWOOD-Ingress-Request", 'NOT-EXTERNAL')

        # Do not log service users calls and internal calls
        user_id = user.id
        is_service_user = user.user_profile.is_service_user
        if not is_service_user and ingress_request == 'EXTERNAL':
            full_path = request.path.strip("/")
            splited_full_path = full_path.split("/")
            request_method = request.method.lower()

            model_class = list_get_or_none(splited_full_path, 1)
            end_point = list_get_or_none(splited_full_path, 2)
            first_arg = list_get_or_none(splited_full_path, 3)
            second_arg = list_get_or_none(splited_full_path, 4)
            payload = None
            is_multipart = request.content_type == "multipart/form-data"
            if request_method == 'post' and not is_multipart:
                payload = request.body[:300]
            log_api_request(
                user_id=user_id,
                permission_check='ok',
                model_class=model_class,
                request_method=request_method,
                path=full_path,
                end_point=end_point,
                first_arg=first_arg,
                second_arg=second_arg,
                payload=payload)
