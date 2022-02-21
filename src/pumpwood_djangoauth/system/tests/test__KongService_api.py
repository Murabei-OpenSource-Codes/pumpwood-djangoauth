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
microservice = PumpWoodMicroService(
    name="test", server_url='http://localhost:8000/')


class TestKongServiceAPI(unittest.TestCase):
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

    def test__list(self):
        microservice.list(
            model_class="KongService", auth_header=auth_header)

    def test__list_without_pag(self):
        microservice.list_without_pag(
            model_class="KongService", auth_header=auth_header)

    def test__fill_options(self):
        microservice.fill_options(
            model_class="KongService", auth_header=auth_header)

    def test__save(self):
        request_data = {
            "model_class": "KongService",
            "service_url": "http://pumpwood-auth-app:5000/teste-url/",
            "service_name": "service-teste",
            "description": "Serviço de testes",
            "notes": "Notes para o Serviço de testes",
            "dimentions": {}}
        results = microservice.save(request_data, auth_header=auth_header)
        self.assertNotEqual(results["service_kong_id"], None)

        pk = results["pk"]
        results = microservice.save(request_data, auth_header=auth_header)
        self.assertEqual(pk, results["pk"])

        routes_dict = microservice.list_registered_routes(
            auth_header=auth_header)
        self.assertIn(results["service_name"], routes_dict.keys())

        endpoints = microservice.list_registered_endpoints(
            auth_header=auth_header)
        len(endpoints)
