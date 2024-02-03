"""Define .config objects for django app."""
import os
from pumpwood_communication.microservices import PumpWoodMicroService
from pumpwood_miscellaneous.storage import PumpWoodStorage
from pumpwood_miscellaneous.rabbitmq import PumpWoodRabbitMQ
from pumpwood_kong.kong_api import KongAPI
# from pumpwood_i8n.singletons import pumpwood_i8n


# Create an Kong api using API_GATEWAY_URL enviroment variable
API_GATEWAY_URL = os.environ.get("API_GATEWAY_URL")
kong_api = KongAPI(api_gateway_url=API_GATEWAY_URL)

# Getting secrets from enviroment variables
MICROSERVICE_NAME = os.environ.get("MICROSERVICE_NAME")
MICROSERVICE_URL = os.environ.get("MICROSERVICE_URL")
MICROSERVICE_USERNAME = os.environ.get("MICROSERVICE_USERNAME")
MICROSERVICE_PASSWORD = os.environ.get("MICROSERVICE_PASSWORD")
microservice = None
microservice_no_login = None
if MICROSERVICE_URL is not None:
    microservice_no_login = PumpWoodMicroService(
        name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
        verify_ssl=False)
    if MICROSERVICE_USERNAME is not None:
        microservice = PumpWoodMicroService(
            name=MICROSERVICE_NAME, server_url=MICROSERVICE_URL,
            username=MICROSERVICE_USERNAME, password=MICROSERVICE_PASSWORD,
            verify_ssl=False)
else:
    print("PumpWoodMicroService not set")

# Storage Object
STORAGE_TYPE = os.environ.get('STORAGE_TYPE')
STORAGE_BUCKET_NAME = os.environ.get('STORAGE_BUCKET_NAME')
STORAGE_BASE_PATH = os.environ.get('STORAGE_BASE_PATH', 'pumpwood_auth')
storage_object = None
if STORAGE_TYPE is not None:
    storage_object = PumpWoodStorage(
        storage_type=STORAGE_TYPE, bucket_name=STORAGE_BUCKET_NAME,
        base_path=STORAGE_BASE_PATH)
else:
    print("PumpWoodStorage not set")

# MEDIA_URL
MEDIA_URL = os.environ.get('MEDIA_URL', 'media/')

# RabbitMQ
RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', "5672"))
rabbitmq_api = None
if RABBITMQ_HOST is not None:
    rabbitmq_api = PumpWoodRabbitMQ(
        username=RABBITMQ_USERNAME, password=RABBITMQ_PASSWORD,
        host=RABBITMQ_HOST, port=RABBITMQ_PORT)
else:
    print("PumpWoodRabbitMQ not set")

# Loggin using RabbitMQ and consumer container
PUMPWOOD_AUTH_IS_RABBITMQ_LOG = os.getenv(
    'PUMPWOOD_AUTH_IS_RABBITMQ_LOG', "FALSE") == 'TRUE'


# # Initiante I8n using django model as backend
# pumpwood_i8n.init(microservice=microservice)
