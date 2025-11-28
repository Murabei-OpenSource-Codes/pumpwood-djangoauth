"""Auxiliary view for MFA."""

__docformat__ = "google"
from .code import create_new_mfa_code, CodeLoginView
from .oauth2 import oauth2_get_authorization_url, SSOLoginView


__all__ = [
    create_new_mfa_code, CodeLoginView,
    oauth2_get_authorization_url, SSOLoginView]
