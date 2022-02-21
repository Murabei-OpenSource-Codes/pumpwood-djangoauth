# -*- coding: utf-8 -*-
import requests
from pumpwood_flaskmisc.testing import TestPumpWood


class TestLoginCases(TestPumpWood):
    load_balancer_address = 'http://localhost:8080/'
    apps_to_regenerate = ['pumpwood-auth-app']
    session = requests.session()
    session.headers.update(
        {'Authorization': 'Token 6cab4ba54bb8f92af7e135d7ad8c7d70d4555f7f'})
    auth_header = {
        'Authorization': 'Token 6cab4ba54bb8f92af7e135d7ad8c7d70d4555f7f'}

    def test__correct_login(self):
        """
        Verifica se usuários estão logando com username e password corretos.
        """
        url = 'http://localhost:8000/' + 'rest/registration/login/'
        response_1 = requests.post(url, json={
                "username": "pumpwood-estimation-app",
                "password": "pass:12345-estimation-app"})
        response_1.raise_for_status()

    def test__incorrect_login(self):
        """
        Verifica se usuários não estão logando com username e password
        incorretos.
        """
        url = 'http://localhost:8000/' + 'rest/registration/login/'
        response_1 = requests.post(url, json={
                "username": "pumpwood-estimation-app",
                "password": "password-errado"})
        self.assertEqual(response_1.status_code, 400)
        resp_data = response_1.json()
        self.assertEqual(
            resp_data["non_field_errors"][0],
            'Unable to log in with provided credentials.')

    def test__blank_password(self):
        """
        Check error response for blank password.
        # """
        url = 'http://localhost:8000/' + 'rest/registration/login/'
        response_1 = requests.post(url, json={
            "username": "user1",
            "password": ""})
        self.assertEqual(response_1.status_code, 400)
        resp_data = response_1.json()
        self.assertEqual(
            resp_data["password"][0], 'This field may not be blank.')

    def test__none_password(self):
        """
        Check error response for None password.
        """
        url = 'http://localhost:8000/' + 'rest/registration/login/'
        response_1 = requests.post(url, json={
            "username": "user1",
            "password": None})
        self.assertEqual(response_1.status_code, 400)
        resp_data = response_1.json()
        self.assertEqual(
            resp_data["password"][0], 'This field may not be null.')

    def check_token_refreshing(self):
        '''
        Verifica se o token está sendo atualizado toda a vez que o usuário
        não microserviço faz login na aplicação quando não é micro-serviço.
        No caso de usuário microserviço o token não é atualizado
        todas as vezes.
        '''
        url = 'http://localhost:8000/' + 'rest/registration/login/'
        response_1 = requests.post(url, json={
                "username": "pumpwood-estimation-app",
                "password": "pass:12345-estimation-app"})
        ex_token = response_1.json()['token']

        response_1 = requests.post(url, json={
                "username": "pumpwood-estimation-app",
                "password": "pass:12345-estimation-app"})
        new_token = response_1.json()['token']
        self.assertNotEqual(ex_token, new_token)

    def check_token_not_refreshing_microservice(self):
        resp_microservice1 = self.session.post(
            '/rest/registration/login/', {
                "username": "microservice1",
                "password": "microservice1"},
            format='json')
        ex_token = resp_microservice1.data['token']

        resp_microservice1 = self.session.post(
            '/rest/registration/login/', {
                "username": "microservice1",
                "password": "microservice1"},
            format='json')
        new_token = resp_microservice1.data['token']
        self.assertEqual(ex_token, new_token)

    def test__check_logged(self):
        '''
        Verifica se colocando o header autentication token no session o
        usuário passa a ser identificado de forma correta.
        '''
        # Ordinary user check
        response = requests.post(
            'http://0.0.0.0:8000/rest/registration/login/', json={
                "username": "user1", "password": "pass:12345-user1"})
        response.raise_for_status()
        response_data = response.json()

        new_header = {
            "Authorization": 'Token ' + response_data['token']}
        check = requests.get(
            'http://0.0.0.0:8000/rest/registration/check/',
            headers=new_header)
        check.raise_for_status()
        check_data = check.json()
        self.assertTrue(check_data)

    def test__check_logged_microservice(self):
        # Microservice check
        response = self.session.post(
            'http://0.0.0.0:8000/rest/registration/login/', json={
                "username": "microservice1",
                "password": "pass:12345-nao-deixa-o-pass"})
        response.raise_for_status()
        response_data = response.json()

        new_header = {
            "Authorization": 'Token ' + response_data['token']}
        check = self.session.get(
            'http://0.0.0.0:8000/rest/registration/check/',
            headers=new_header)
        check.raise_for_status()
        self.assertTrue(check.json())

    def test__logout_and_check(self):
        'Verifica se os usuários estão deslogando da base'
        # Ordinary user check
        response = self.session.post(
            'http://0.0.0.0:8000/rest/registration/login/', json={
                "username": "user1", "password": "pass:12345-user1"})
        response.raise_for_status()
        response_data = response.json()

        new_header = {
            "Authorization": 'Token ' + response_data['token']}
        response_logout = self.session.get(
            'http://0.0.0.0:8000/rest/registration/logout/',
            headers=new_header)
        response_logout.raise_for_status()

        response_check = self.session.get(
            'http://0.0.0.0:8000/rest/registration/check/',
            headers=new_header)
        self.assertEqual(response_check.status_code, 401)

    def test__logout_and_check_microservice(self):
        'Verifica se os microservice estão deslogando da base'
        # Microservice check
        response = self.session.post(
            'http://0.0.0.0:8000/rest/registration/login/', json={
                "username": "microservice1",
                "password": "pass:12345-nao-deixa-o-pass"})
        response.raise_for_status()
        response_data = response.json()

        new_header = {
            "Authorization": 'Token ' + response_data['token']}
        response_logout = self.session.get(
            'http://0.0.0.0:8000/rest/registration/logout/',
            headers=new_header)

        response_check = self.session.get(
            'http://0.0.0.0:8000/rest/registration/check/',
            headers=new_header)
        self.assertEqual(response_check.status_code, 401)
