# coding=utf-8
import datetime
import requests
from pumpwood_flaskmisc.testing import TestPumpWood
from pumpwood_communication.microservices import PumpWoodMicroService


class TestRegistrationAPI(TestPumpWood):
    load_balancer_address = 'http://localhost:8080/'
    apps_to_regenerate = ['pumpwood-auth-app']
    session = requests.session()
    session.headers.update(
        {'Authorization': 'Token 6cab4ba54bb8f92af7e135d7ad8c7d70d4555f7f'})
    auth_header = {
        'Authorization': 'Token 6cab4ba54bb8f92af7e135d7ad8c7d70d4555f7f'}

    def test_signup(self):
        microservice = PumpWoodMicroService(
            server_url="http://0.0.0.0:8000/")
        request_payload = {
            'username': "teste-usuario1234",
            'password': "Pass-word:123@",
            'email': "teste-usuario1234@email.com",
            'first_name': 'first_name 1234',
            'last_name': 'last_name 12344'}
        response = self.session.post(
            "http://0.0.0.0:8000/rest/registration/signup/",
            json=request_payload)
        response.raise_for_status()
        response_data = response.json()

        created_user = microservice.retrieve(
            model_class="User", pk=response_data["pk"],
            auth_header=self.auth_header)
        self.assertEqual(
            request_payload["username"], created_user['username'])
        self.assertEqual(
            request_payload["email"], created_user['email'])
        self.assertEqual(
            request_payload["first_name"], created_user['first_name'])
        self.assertEqual(
            request_payload["last_name"], created_user['last_name'])

    def test_create_activation_link(self):
        url_template = (
            "http://0.0.0.0:8000/rest/registration/"
            "newactivationlink/{user_id}")
        response = self.session.get(url_template.format(user_id=30))
        response.raise_for_status()

    def test_update_activation_link(self):
        url_template = (
            "http://0.0.0.0:8000/rest/registration/"
            "newactivationlink/{user_id}")
        response = self.session.get(url_template.format(user_id=31))
        response.raise_for_status()
