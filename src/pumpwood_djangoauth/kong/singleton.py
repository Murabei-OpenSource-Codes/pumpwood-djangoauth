"""Define singletons objects for django app."""
import os
from pumpwood_kong.kong_api import KongAPI


# Create an Kong api using API_GATEWAY_URL enviroment variable
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL")
kong_api = KongAPI(api_gateway_url=API_GATEWAY_URL)
