import datetime
import requests
import unittest
from pumpwood_flaskmisc.testing import TestPumpWood
from pumpwood_communication.microservices import PumpWoodMicroService


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

    def test__get_kong_routes(self):
        microservice = PumpWoodMicroService(
            server_url='http://localhost:8000/')
        microservice.list_registered_routes(auth_header=auth_header)

    def test__dummy_api(self):
        json_resp = session.get(
            'http://localhost:8000/rest/pumpwood/dummy-call/').json()
        json_resp = session.post(
            'http://localhost:8000/rest/pumpwood/dummy-call/',
            json={"teste": "payload"}).json()
