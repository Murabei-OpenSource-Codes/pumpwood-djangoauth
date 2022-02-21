import datetime
import requests
import unittest
from pumpwood_flaskmisc.testing import TestPumpWood
from pumpwood_communication.microservices import PumpWoodMicroService
from core.singletons import kong_api, register_auth_kong_objects


session = requests.session()
session.headers.update(
    {'Authorization': 'Token 6cab4ba54bb8f92af7e135d7ad8c7d70d4555f7f'})
auth_header = {
    'Authorization': 'Token 6cab4ba54bb8f92af7e135d7ad8c7d70d4555f7f'}


class TestRegistrationAPI(unittest.TestCase):
    session = requests.session()
    session.headers.update(
        {'Authorization': 'Token 6cab4ba54bb8f92af7e135d7ad8c7d70d4555f7f'})

    load_balancer_address = "http://0.0.0.0:8080/"
    'Ip of the load balancer'
    apps_to_regenerate = ['pumpwood-auth-app']
    'Name of the apps to be regenerated after the test is over'

    test_address = "http://0.0.0.0:5000/"

    def setUp(self, *args, **kwargs):
        """Regen the database in the setUp calling reload end-point."""
        ######################
        # Regenerate database#
        for app in self.apps_to_regenerate:
            path = 'reload-db/' + app + '/'
            response = requests.get(self.load_balancer_address + path)
            if response.status_code != 200:
                raise Exception(app + ' regenerate: ', response.text)

    def test__create_base_endpoints(self):
        service_url = "http://pumpwood-auth-app:5000/"
        api_gateway_url = "http://localhost:8001/"
        auth_static_service = "http://pumpwood-auth-admin-static:5000"
        service_name = "pumpwood-auth-app"
        health_check = "/health-check/pumpwood-auth-app/"

        register_auth_kong_objects(
            routes=[{
                "route_url": "/rest/registration/",
                "route_name": "pumpwood-auth-app--registration",
                "route_type": "aux",
                "description": "Registration",
                "notes": (
                    "End-point for login, logout and other Authentication "
                    "functions"),
                "dimentions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "authentication",
                    "endpoint": "registration",
                    "route_type": "aux"},
                "icon": ""
            }, {
                "route_url": "/rest/pumpwood/",
                "route_name": "pumpwood-auth-app--pumpwood",
                "route_type": "aux",
                "description": "Pumpwood System",
                "notes": (
                    "System related end-points to list Kong routes, and "
                    "dummy-calls"),
                "dimentions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "system",
                    "endpoint": "pumpwood",
                    "route_type": "aux"},
                "icon": ""
            }, {
                "route_url": "/rest/kongservice/",
                "route_name": "pumpwood-auth-app--kongservice",
                "route_type": "endpoint",
                "description": "Microservice Services",
                "notes": (
                    "Microservices registred on Pumpwood."),
                "dimentions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "system",
                    "endpoint": "kongservice",
                    "route_type": "endpoint"},
                "icon": ""
            }, {
                "route_url": "/rest/kongroute/",
                "route_name": "pumpwood-auth-app--kongroute",
                "route_type": "endpoint",
                "description": "Microservice Routes",
                "notes": (
                    "Routes registred on Pumpwood, each one"),
                "dimentions": {
                    "microservice": "pumpwood-auth-app",
                    "service_type": "core",
                    "function": "system",
                    "endpoint": "kongroute",
                    "route_type": "endpoint"},
                "icon": ""
            }]
        )
