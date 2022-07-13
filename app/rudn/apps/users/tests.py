from urllib.parse import urlparse, parse_qs
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from rest_framework.reverse import reverse_lazy
from django.test import override_settings
from rest_framework import status
from django.core import mail
from django.test import TestCase
import re

from apps.users.services import AuthAppService

User = get_user_model()

locmem_email_backend = override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
)


class AuthApiTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        print('setUpTestData')
        data = {
            'username': 'admin',
            'email': 'admin@test.ru',
            'password': make_password('string19'),
            'keyword': 'test',
        }
        cls.user = User.objects.create(**data)
        cls.user.emailaddress_set.create(email=cls.user.email, primary=True, verified=True)

    def test_sign_in(self):
        url = reverse_lazy('apps.users:api_login')

        data = {
            'email': self.user.email,
            'password': 'string19',
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    def test_sign_in_bad_request(self):
        url = reverse_lazy('apps.users:api_login')
        data = {
            'email': self.user.email,
            'password': 'string11',
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)
        self.assertEqual(response.data, {'detail': 'No active account found with the given credentials'})

    def test_sign_is_not_active(self):
        self.user.is_active = False
        self.user.save()

        url = reverse_lazy('apps.users:api_login')
        data = {
            'email': self.user.email,
            'password': 'string19',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED, response.data)
        self.assertEqual(response.data, {'detail': 'No active account found with the given credentials'})

    def test_sigh_up(self):
        url = reverse_lazy('apps.users:api_sign_up')
        data = {
            'username': 'bob',
            'email': 'oemr@mail.ru',
            'password1': 'string19',
            'password2': 'string18',
            'keyword': 'test',
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, response.data)
        self.assertEqual(response.json(), {'password2': ["The two password fields didn't match."]})

        data['password2'] = 'string19'
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        user = AuthAppService.get_user('oemr@mail.ru')
        self.assertFalse(user.is_active)
        url = reverse_lazy('apps.users:api_login')

        data = {
            'email': self.user.email,
            'password': 'string19',
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

    @locmem_email_backend
    def test_password_reset(self):
        url = reverse_lazy('apps.users:forgot_password')
        data = {'email': self.user.email}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)

        self.assertEqual(len(mail.outbox), 1)
        url_conf = reverse_lazy('apps.users:password_reset_confirm')
        string = str(mail.outbox[0].message())
        pattern = r'(http?://[^\"\s]+)'
        result = re.findall(pattern, string)
        reset_url = result[2].replace('&amp;', '&')
        print(reset_url)
        parsed = urlparse(reset_url)
        query_params = parse_qs(parsed.query)
        print(query_params)

        data = {
            "new_password": "string1986",
            **query_params
        }
        print(data)
        response = self.client.post(url_conf, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)
        print(response.data)
        url = reverse_lazy('apps.users:api_login')

        data = {
            'email': self.user.email,
            'password': 'string1986',
        }
        response = self.client.post(url, data, format='json')
        print(response.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK, response.data)


class UserModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        data = {
            'username': 'admin',
            'email': 'user@test.com',
            'password': make_password('string19'),
            'keyword': 'test',
        }
        cls.user = User.objects.create(**data, is_active=False)
        cls.user.emailaddress_set.create(email=cls.user.email, primary=True, verified=True)

    def test_user_str(self):
        email = str(self.user)
        self.assertEqual(email, 'user@test.com')
