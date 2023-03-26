"""Define .config objects for django app."""
import os
from pumpwood_communication.microservices import PumpWoodMicroService
from pumpwood_miscellaneous.storage import PumpWoodStorage
from pumpwood_kong.kong_api import KongAPI

# Create an Kong api using API_GATEWAY_URL enviroment variable
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL")
kong_api = KongAPI(api_gateway_url=API_GATEWAY_URL)

# Getting secrets from enviroment variables
MICROSERVICE_NAME = os.environ.get("MICROSERVICE_NAME")
MICROSERVICE_URL = os.environ.get("MICROSERVICE_URL")
MICROSERVICE_USERNAME = os.environ.get("MICROSERVICE_USERNAME")
MICROSERVICE_PASSWORD = os.environ.get("MICROSERVICE_PASSWORD")

microservice = PumpWoodMicroService(
    name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
    username=MICROSERVICE_USERNAME, password=MICROSERVICE_PASSWORD,
    verify_ssl=False)
microservice_no_login = PumpWoodMicroService(
    name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
    verify_ssl=False)

# Storage Object
storage_type = os.environ.get('STORAGE_TYPE')
bucket_name = os.environ.get('STORAGE_BUCKET_NAME')
base_path = os.environ.get('STORAGE_BASE_PATH', 'pumpwood_auth')
storage_object = PumpWoodStorage(
    storage_type=storage_type, bucket_name=bucket_name,
    base_path=base_path)

# MEDIA_URL
MEDIA_URL = os.environ.get('MEDIA_URL', 'media/')
