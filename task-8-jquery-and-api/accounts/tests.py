from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class UserManagerTest(TestCase):
    def test_create_user(self):
        User = get_user_model()
        user = User.objects.create_user(
            username="testuser", email="test@kuaz.info", password="testpass", age=55
        )
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@kuaz.info")
        self.assertEqual(user.age, 55)
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        User = get_user_model()
        user = User.objects.create_superuser(
            username="testadmin",
            email="testadmin@kuaz.info",
            password="testpass",
            age=56,
        )
        self.assertEqual(user.username, "testadmin")
        self.assertEqual(user.email, "testadmin@kuaz.info")
        self.assertEqual(user.age, 56)
        self.assertTrue(user.is_active)
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)


class SignupPageTest(TestCase):
    def test_url_exists_at_correct_location_signupview(self):
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_view_name(self):
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_form(self):
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser1",
                "email": "testuser1@kuaz.info",
                "password1": "testpass1234567",
                "password2": "testpass1234567",
                "age": 18,
            },
        )
        self.assertEqual(response.status_code, 302)
        User = get_user_model()
        self.assertEqual(User.objects.all().count(), 1)
        self.assertEqual(User.objects.all()[0].get_username(), "testuser1")
        self.assertEqual(User.objects.all()[0].email, "testuser1@kuaz.info")
