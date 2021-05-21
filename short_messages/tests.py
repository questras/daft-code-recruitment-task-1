from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.urls import reverse
from django.contrib.auth import get_user_model

from .models import ShortMessage

User = get_user_model()


def create_test_user():
    """Create a test user for testing purposes."""
    return User.objects.create(username='test_username', password='test_password')


def authorize_user(case: APITestCase, user: User):
    """Authorize given user in given test case so the requests
    will be authorized."""

    token = Token.objects.create(user=user)
    case.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')


class ShortMessageModelTests(APITestCase):
    def setUp(self) -> None:
        self.message = ShortMessage.objects.create(body="test")

    def test_reset_views_sets_views_counter_to_zero(self):
        self.message.views_counter = 100
        self.message.save()
        before = ShortMessage.objects.get(id=self.message.id)
        self.assertEqual(before.views_counter, 100)

        self.message.reset_views()

        after = ShortMessage.objects.get(id=self.message.id)
        self.assertEqual(after.views_counter, 0)

    def test_increment_views_changes_views_counter_by_one(self):
        before = ShortMessage.objects.get(id=self.message.id)
        self.assertEqual(before.views_counter, 0)

        result = self.message.increment_views()
        self.assertEqual(result, 1)

        after = ShortMessage.objects.get(id=self.message.id)
        self.assertEqual(after.views_counter, 1)

    def test_correct_str_method(self):
        body = 'test-body'
        views_counter = 100
        expected = f'"{body}" - {views_counter} views.'
        message = ShortMessage.objects.create(
            body=body,
            views_counter=views_counter
        )

        self.assertEqual(str(message), expected)


class CreateShortMessageEndpointTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_test_user()
        self.url = reverse('shortmessage-list')
        self.data = {
            'body': 'test-body'
        }

    def test_unauthenticated_user_cannot_create(self):
        r = self.client.post(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ShortMessage.objects.all().count(), 0)

    def test_can_create_with_correct_body(self):
        authorize_user(self, self.user)
        r = self.client.post(self.url, self.data)

        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShortMessage.objects.all().count(), 1)

        message = ShortMessage.objects.all()[0]
        self.assertEqual(message.body, self.data['body'])
        self.assertEqual(message.views_counter, 0)

    def test_specified_views_counter_in_request_data_doesnt_work(self):
        """Test whether specifying `views_counter` in request data
        has no effect on newly created message."""
        authorize_user(self, self.user)

        self.data['views_counter'] = 100

        r = self.client.post(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ShortMessage.objects.all().count(), 1)

        self.assertEqual(r.json()['views_counter'], 0)
        self.assertEqual(ShortMessage.objects.all()[0].views_counter, 0)

    def test_cannot_create_message_with_empty_body(self):
        authorize_user(self, self.user)
        self.data['body'] = ''

        r = self.client.post(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ShortMessage.objects.all().count(), 0)

    def test_cannot_create_message_with_too_long_body(self):
        authorize_user(self, self.user)
        body_length = 161  # One more than maximum length.
        self.data['body'] = body_length * 't'

        r = self.client.post(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ShortMessage.objects.all().count(), 0)


class DeleteShortMessageEndpointTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_test_user()
        self.message = ShortMessage.objects.create(body='test')
        self.url = reverse('shortmessage-detail', args=(self.message.id,))

    def test_unauthenticated_user_cannot_delete(self):
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ShortMessage.objects.all().count(), 1)

    def test_can_delete_message(self):
        authorize_user(self, self.user)

        self.assertEqual(ShortMessage.objects.all().count(), 1)
        r = self.client.delete(self.url)
        self.assertEqual(r.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ShortMessage.objects.all().count(), 0)

    def test_deleting_non_existing_message_returns_404_code(self):
        authorize_user(self, self.user)
        self.assertEqual(ShortMessage.objects.all().count(), 1)

        new_url = reverse('shortmessage-detail', args=(self.message.id + 1,))
        r = self.client.delete(new_url)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(ShortMessage.objects.all().count(), 1)


class UpdateShortMessageEndpointTests(APITestCase):
    def setUp(self) -> None:
        self.user = create_test_user()
        self.message = ShortMessage.objects.create(
            body='test',
            views_counter=100
        )
        self.url = reverse('shortmessage-detail', args=(self.message.id,))
        self.data = {
            'body': 'updated-body'
        }

    def test_unauthenticated_user_cannot_update(self):
        r = self.client.put(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_can_update_with_correct_data(self):
        authorize_user(self, self.user)

        r = self.client.put(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        message = ShortMessage.objects.get(id=self.message.id)
        self.assertEqual(message.body, self.data['body'])

    def test_views_counter_is_reset_to_zero_after_update(self):
        authorize_user(self, self.user)

        self.assertNotEqual(self.message.views_counter, 0)
        r = self.client.put(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        message = ShortMessage.objects.get(id=self.message.id)
        self.assertEqual(message.views_counter, 0)

    def test_cannot_update_with_empty_body(self):
        authorize_user(self, self.user)
        self.data['body'] = ''

        r = self.client.put(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        message = ShortMessage.objects.get(id=self.message.id)
        # Everything unchanged.
        self.assertEqual(message.body, self.message.body)
        self.assertEqual(message.views_counter, self.message.views_counter)

    def test_cannot_update_with_too_long_body(self):
        authorize_user(self, self.user)
        body_length = 161  # One more than maximum length.
        self.data['body'] = body_length * 't'

        r = self.client.put(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        message = ShortMessage.objects.get(id=self.message.id)
        # Everything unchanged.
        self.assertEqual(message.body, self.message.body)
        self.assertEqual(message.views_counter, self.message.views_counter)

    def test_specified_views_counter_in_request_data_doesnt_work(self):
        """Test whether specifying `views_counter` in request data
        has no effect on updated message."""
        authorize_user(self, self.user)

        self.data['views_counter'] = 42
        r = self.client.put(self.url, self.data)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        message = ShortMessage.objects.get(id=self.message.id)
        self.assertEqual(message.body, self.data['body'])
        # Views counter is correctly reset.
        self.assertEqual(message.views_counter, 0)


class ReadShortMessageEndpointTests(APITestCase):
    def setUp(self) -> None:
        self.message = ShortMessage.objects.create(body='test-body')
        self.url = reverse('shortmessage-detail', args=(self.message.id,))

    def test_response_contains_body_and_views_counter(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        self.assertContains(r, 'views_counter')
        self.assertContains(r, 'body')
        self.assertEqual(r.json()['body'], self.message.body)

    def test_views_counter_is_incremented_on_read(self):
        old_views_counter = self.message.views_counter

        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        self.assertEqual(r.json()['views_counter'], old_views_counter + 1)
        self.assertEqual(
            ShortMessage.objects.get(id=self.message.id).views_counter,
            old_views_counter + 1
        )

    def test_reading_non_existing_message_returns_404(self):
        new_url = reverse('shortmessage-detail', args=(self.message.id + 1,))

        r = self.client.get(new_url)
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)


class ListShortMessagesEndpointTests(APITestCase):
    def setUp(self) -> None:
        self.message1 = ShortMessage.objects.create(body='test-body1')
        self.message2 = ShortMessage.objects.create(
            body='test-body2',
            views_counter=100
        )
        self.url = reverse('shortmessage-list')

    def test_response_contains_all_messages(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        self.assertEqual(len(r.json()), 2)
        self.assertContains(r, self.message1.body)
        self.assertContains(r, self.message2.body)

    def test_each_message_in_response_contains_views_counter_and_body(self):
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)

        self.assertEqual(len(r.json()), 2)
        for message in r.json():
            self.assertIn('views_counter', message)
            self.assertIn('body', message)

    def test_listing_messages_doesnt_increment_views_counters(self):
        r = self.client.get(self.url)

        old_views_counter1 = self.message1.views_counter
        old_views_counter2 = self.message2.views_counter

        for message in r.json():
            if message['body'] == self.message1.body:
                self.assertEqual(old_views_counter1, message['views_counter'])
            elif message['body'] == self.message2.body:
                self.assertEqual(old_views_counter2, message['views_counter'])
            else:
                # Something went wrong and body of
                # message doesn't match any message
                self.assertTrue(False)

    def test_when_no_messages_then_empty_list_is_returned(self):
        self.message1.delete()
        self.message2.delete()

        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json(), [])
