from django.test import TestCase
from django.test import Client
from django.urls import reverse
from .models import Login


def create_login_credentials(email, password):
    return {
        'email': email,
        'pwd': password
    }


def create_new_user_data(username, email, password, confirm_password):
    d = create_login_credentials(email, password)
    d.update({'username': username})
    d.update({'pwd1': confirm_password})
    return d


class Test_Login(TestCase):
    USER = Login().create_login({'email': 'rajan@bing.com', 'username': 'Sundar'})

    def create_new_user(self):
        data = create_new_user_data('Sundar', 'rajan@bing.com', 'valid123', 'valid123')
        return self.create_new_user_with_data(data)

    def create_new_user_with_data(self, data):
        client = Client()
        r = client.post(reverse('events:new_user'), data)
        return r

    def test_default(self):
        r = self.client.get(reverse('events:login'))
        print(r.status_code)
        self.assertEqual(r.status_code, 200, 'invalid status')

    def test_create_new_user(self):
        res = self.create_new_user()
        login = res.context['user']
        self.assertEqual(login.username, self.USER.username, 'Invalid response')
        self.assertEqual(login.email, self.USER.email, 'Invalid response')

    def test_create_new_user_with_invalid_username(self):
        data = create_new_user_data('as', 'rajan@bing.com', 'abcdefg', 'abcdefg')
        res = self.create_new_user_with_data(data)
        err = res.context['err']
        self.assertEqual(err, 'Valid username with 3 or more characters required')

    def test_create_new_user_with_invalid_email(self):
        data = create_new_user_data('asd', 'r@b.com', 'abcdefg', 'abcdefg')
        res = self.create_new_user_with_data(data)
        err = res.context['err']
        self.assertEqual(err, 'Valid email with 8 or more characters required')

    def test_create_new_user_with_invalid_password_length(self):
        data = create_new_user_data('asd', 'rajan@bing.com', 'abcde', 'abcde')
        res = self.create_new_user_with_data(data)
        err = res.context['err']
        self.assertEqual(err, 'password must have 6 or more characters')

    def test_create_new_user_with_password_confirm_password_mismatch(self):
        data = create_new_user_data('asd', 'rajan@bing.com', 'abcdef', 'abcdeg')
        res = self.create_new_user_with_data(data)
        err = res.context['err']
        self.assertEqual(err, 'password and confirm password do not match')

    def test_invalid_email_login(self):
        self.create_new_user()
        data = create_login_credentials('abc@bing.com', 'abc')
        r = self.client.post(reverse('events:login'), data)
        error = r.context['err']
        self.assertEqual(error, 'Email not recognized. Please register')

    def test_invalid_password(self):
        self.create_new_user()
        data = create_login_credentials('rajan@bing.com', 'abcefg')
        r = self.client.post(reverse('events:login'), data)
        error = r.context['err']
        self.assertEqual(error, 'invalid password')

class Test_Index_Page(TestCase):
    pass
