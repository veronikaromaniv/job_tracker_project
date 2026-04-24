from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse


class RegisterViewTest(TestCase):

    def test_register_page_loads(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_redirects_if_logged_in(self):
        User.objects.create_user(username='existing', password='pass1234')
        self.client.login(username='existing', password='pass1234')
        response = self.client.get(reverse('register'))
        self.assertRedirects(response, reverse('dashboard'))

    def test_successful_registration(self):
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'strongpass123',
            'password2': 'strongpass123',
        })
        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(User.objects.filter(username='newuser').exists())


class ProfileViewTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='pass1234', email='old@example.com'
        )
        self.client.login(username='testuser', password='pass1234')

    def test_profile_page_loads(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/accounts/', response['Location'])

    def test_update_info(self):
        response = self.client.post(reverse('profile'), {
            'action': 'update_info',
            'first_name': 'Іванна',
            'last_name': 'Коваль',
            'email': 'new@example.com',
        })
        self.assertRedirects(response, reverse('profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Іванна')
        self.assertEqual(self.user.email, 'new@example.com')
