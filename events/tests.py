import logging
import logging.handlers
import sys
from datetime import timedelta

from django.test import Client
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Login, Event_Admin, Event


def create_logger(name):
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    return log


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


def create_new_user(data):
    client = Client()
    r = client.post(reverse('events:new_user'), data)
    return r


def create_event():
    # crete event
    event = Event()
    event.event_name = 'My Event'
    event.event_date = timezone.now() + timedelta(days=7)
    event.event_venue = 'Bangalore'
    event.event_managers = 'Sundar'
    event.save()
    return event


def create_event_admin():
    # create event admin
    event_admin = Event_Admin()
    event_admin.admin = 'Sundar'
    event_admin.event_id = 1
    event_admin.save()


def setup():
    create_event()
    create_event_admin()
    data = get_admin_user_data()
    create_new_user(data)
    # login as user
    data = get_normal_user_data()
    create_new_user(data)


def get_admin_user_data():
    return {
        'username': 'Sundar',
        'email': 'sundar@bing.com',
        'pwd': 'valid123',
        'pwd1': 'valid123',

    }


def get_normal_user_data():
    return {
        'username': 'rajan',
        'email': 'rajan@yahoo.com',
        'pwd': 'abcbac',
        'pwd1': 'abcbac',

    }


def get_form_data(event, first_name, last_name, email, mobile, payment_amount,
                  payment_ref, extended_tour, num_guests, num_days, mode_of_travel,
                  arrival_date, departure_date, pickup_reqd, special_req):
    data = {
        'event': event,
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'mobile': mobile,
        'payment_amount': payment_amount,
        'payment_ref': payment_ref,
        'extended_tour': extended_tour,
        'num_of_guests': num_guests,
        'num_of_days': num_days,
        'mode_of_travel': mode_of_travel,
        'arrival_date': arrival_date,
        'departure_date': departure_date,
        'pickup_reqd': pickup_reqd,
        'special_req': special_req

    }
    return data


class Test_Login(TestCase):
    USER = Login().create_login({'email': 'sundar@bing.com', 'username': 'Sundar'})
    LOGGER = create_logger('Test_Login')

    def test_default(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        create_event()
        print(reverse('events:login'))
        r = self.client.get(reverse('events:login'))
        self.assertEqual(r.status_code, 200, 'invalid status')

    def test_create_new_user(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        res = create_new_user(get_admin_user_data())
        login = res.context['user']
        self.assertEqual(login.username, self.USER.username, 'Invalid response')
        self.assertEqual(login.email, self.USER.email, 'Invalid response')

    def test_create_new_user_with_invalid_username(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        data = create_new_user_data('as', 'rajan@bing.com', 'abcdefg', 'abcdefg')
        res = create_new_user(data)
        err = res.context['err']
        self.assertEqual(err, 'Valid username with 3 or more characters required')

    def test_create_new_user_with_invalid_email(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        data = create_new_user_data('asd', 'r@b.com', 'abcdefg', 'abcdefg')
        res = create_new_user(data)
        err = res.context['err']
        self.assertEqual(err, 'Valid email with 8 or more characters required')

    def test_create_new_user_with_invalid_password_length(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        data = create_new_user_data('asd', 'rajan@bing.com', 'abcde', 'abcde')
        res = create_new_user(data)
        err = res.context['err']
        self.assertEqual(err, 'password must have 6 or more characters')

    def test_create_new_user_with_password_confirm_password_mismatch(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        data = create_new_user_data('asd', 'rajan@bing.com', 'abcdef', 'abcdeg')
        res = create_new_user(data)
        err = res.context['err']
        self.assertEqual(err, 'password and confirm password do not match')

    def test_invalid_email_login(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        setup()
        data = create_login_credentials('abc@bing.com', 'abcbac')
        r = self.client.post(reverse('events:login'), data)
        error = r.context['err']
        self.assertEqual(error, 'Email not recognized. Please register')

    def test_invalid_password(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        create_new_user(get_normal_user_data())
        data = create_login_credentials('rajan@yahoo.com', 'abcefg')
        r = self.client.post(reverse('events:login'), data)
        error = r.context['err']
        self.assertEqual(error, 'invalid password')


class Test_Index_Page(TestCase):
    """ Test that all context objects are present as expected """
    LOGGER = create_logger('Test_Index_Page')

    def test_index_context_admin(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        create_event()
        create_event_admin()
        data = get_admin_user_data()
        create_new_user(data)
        # login as admin
        client = Client()
        data = get_admin_user_data()
        print(data)
        r = client.post(reverse('events:login'), data)
        context = r.context
        user = context['user']
        admin = context['admin']
        events = context['events']
        self.assertIsNotNone(user)
        self.assertIsNotNone(admin)
        self.assertIsNotNone(events)
        self.assertEqual(user.username, admin.admin)

    def test_index_context_user(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        setup()
        client = Client()
        r = client.post(reverse('events:login'), get_normal_user_data())
        context: dict = r.context
        self.assertTrue('user' in context)
        self.assertTrue('events' in context)
        self.assertTrue('admin' in context and context['admin'] is None)


class Test_Registration(TestCase):
    LOGGER = create_logger('Test_Registration')

    def test_empty_form(self):
        name = sys._getframe().f_code.co_name
        self.LOGGER.debug(' Testing ' + name)
        setup()
        event = create_event()
        client = Client()
        client.post(reverse('events:login'), get_normal_user_data())
        r = client.get(reverse('events:register', kwargs={'event_id': event.id}))
        self.assertTrue('user' in r.context)
        self.assertTrue('form' in r.context)

    def test_form_post_valid_data(self):
        setup()
        # login
        data = create_login_credentials('rajan@yahoo.com', 'abcbac')
        client = Client()
        r = client.post(reverse('events:login'), data)
        self.assertTrue(r.status_code == 200)

        event = create_event()
        arrival_date = event.event_date
        departure_date = arrival_date + timedelta(days=1)
        post_data = get_form_data(event.id, 'Rajan', 'TK', 'rajan@yahoo.com', '1234567890', '1000', 'qwerty',
                                  'No', '1', '1', 'Road', str(arrival_date), str(departure_date), 'No', 'welcome drink')

        response = client.post(reverse('events:register', kwargs={'event_id': event.id}), post_data)
        context = response.context
        self.assertTrue('user' in context)
        self.assertTrue('event' in context)
        self.assertTrue('registration' in context)

    def common(self, arr_date, dep_date, num_guests, num_days):
        setup()
        # login
        data = create_login_credentials('rajan@yahoo.com', 'abcbac')
        client = Client()
        r = client.post(reverse('events:login'), data)
        self.assertTrue(r.status_code == 200)

        event = create_event()
        post_data = get_form_data(event.id, 'Rajan', 'TK', 'rajan@yahoo.com', '1234567890', '1000', 'qwerty',
                                  'No', num_guests, num_days, 'Road', arr_date, dep_date, 'No', 'welcome drink')

        response = client.post(reverse('events:register', kwargs={'event_id': event.id}), post_data)
        context = response.context
        self.assertTrue('user' in context)
        self.assertTrue('event' in context)
        self.assertTrue('err' in context)
        self.assertFalse('registration' in context)
        self.assertEqual(context['err'], 'Either dates are not valid or number of guests or number of days is invalid.')

    def test_form_post_arr_date_past_event_date(self):
        event = create_event()
        arrival_date = event.event_date + timedelta(days=1)
        departure_date = arrival_date + timedelta(days=1)
        num_guests = 1
        num_days = 1
        self.common(arrival_date, departure_date, num_guests, num_days)

    def test_form_post_arr_date_past_dep_date(self):
        event = create_event()
        departure_date = event.event_date
        arrival_date = departure_date + timedelta(days=1)
        num_guests = 1
        num_days = 1
        self.common(arrival_date, departure_date, num_guests, num_days)

    def test_form_post_num_guests_zero(self):
        event = create_event()
        arrival_date = event.event_date
        departure_date = arrival_date + timedelta(days=1)
        num_guests = 0
        num_days = 1
        self.common(arrival_date, departure_date, num_guests, num_days)

    def test_form_post_num_days_zero(self):
        event = create_event()
        arrival_date = event.event_date
        departure_date = arrival_date + timedelta(days=1)
        num_guests = 1
        num_days = 0
        self.common(arrival_date, departure_date, num_guests, num_days)
