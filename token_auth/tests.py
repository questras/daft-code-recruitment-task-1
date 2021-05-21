from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class RegisterViewTests(APITestCase):
    def setUp(self):
        self.data = {
            'username': 'testusername',
            'password': 'valid_complicated_password123',
        }
        self.url = reverse('register')

    def test_reject_weak_passwords(self):
        """Test whether weak passwords are rejected."""

        weak_passwords = [
            '123123123',  # only numbers,
            'test',  # too short,
            'password'  # too common
        ]

        # Initially there are no users created.
        self.assertEqual(User.objects.all().count(), 0)

        for password in weak_passwords:
            self.data['password'] = password
            r = self.client.post(self.url, self.data)
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            # No user was created.
            self.assertEqual(User.objects.all().count(), 0)

    def test_correct_data_can_create_user(self):
        r = self.client.post(self.url, self.data)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 1)

        user = User.objects.get(username=self.data['username'])
        self.assertTrue(user.check_password(self.data['password']))

    def test_cannot_create_user_with_blank_username(self):
        self.data['username'] = ''

        self.assertEqual(User.objects.all().count(), 0)
        r = self.client.post(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.all().count(), 0)

    def test_cannot_create_user_with_blank_password(self):
        self.data['password'] = ''

        self.assertEqual(User.objects.all().count(), 0)
        r = self.client.post(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.all().count(), 0)

    def test_cannot_create_user_with_existing_username(self):
        existing_user = User.objects.create(**self.data)

        self.assertEqual(User.objects.all().count(), 1)
        r = self.client.post(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(User.objects.all().count(), 1)
