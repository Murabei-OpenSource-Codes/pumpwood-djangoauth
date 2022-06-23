"""Singletons for microservice comunication."""
import os
from pumpwood_communication.microservices import PumpWoodMicroService

#############################################
# Getting secrets from enviroment variables #
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
