import random
import string

from django.contrib.auth.models import User
from django.test import TestCase


class LongerUsernameAndEmailTests(TestCase):
    """
    Unit tests for longerusernameandemail app
    """

    def setUp(self):
        """
        creates a user with a terribly long username
        """
        long_username = ''.join([str(i) for i in range(100)])

        self.user = User.objects.create_user(
            'test%s' % long_username,
            '%s@example.com' % long_username,
            'testpassword'
        )

    def testUserCreation(self):
        """
        tests that self.user was successfully saved, and can be retrieved
        """
        self.assertNotEqual(self.user, None)

        # returns DoesNotExist error if the user wasn't created
        User.objects.get(id=self.user.id)


class LongerUsernameAndEmailAdminTests(TestCase):
    """
    Functional tests for the django admin when longerusernameandemail
    is enabled.
    """

    urls = 'longerusernameandemail.tests.urls'

    email = 'superuserusername@example.com'
    password = 'superuserpassowrd'

    def setUp(self):
        # create two users with long usernames & emails
        self.user1 = User.objects.create_user(
            'test%s' % self._get_long(),
            '%s@example.com' % self._get_long(),
            'testpassword',
        )
        self.user2 = User.objects.create_user(
            'test%s' % self._get_long(),
            '%s@example.com' % self._get_long(),
            'testpassword',
        )

        # create superuser to do the actions, and log in as them
        User.objects.create_superuser(self.email, self.email, self.password)
        self.client.login(username=self.email, password=self.password)

    def _get_long(self, alpha=string.ascii_letters, length=100):
        "get a long, randmon string"
        return ''.join([random.choice(alpha) for i in range(length)])

    def test_read_user_list(self):
        "test we can read the list of users in the admin"
        resp = self.client.get('/admin/auth/user/')
        self.assertEqual(resp.status_code, 200)

    def test_read_user(self):
        "test we can read a particular user in the admin"
        url = '/admin/auth/user/{}/'.format(self.user1.pk)
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    def test_create_user(self):
        "test we can create a new user using the admin"
        org_user_count = User.objects.count()
        resp = self.client.post('/admin/auth/user/add/', data={
            'username': 'test{}@example.com'.format(self._get_long()),
            'email': 'test{}@example.com'.format(self._get_long()),
            'password1': 'test',
            'password2': 'test',
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(User.objects.count(), org_user_count + 1)

    def test_edit_user(self):
        "test we can edit a particular user using the admin"
        new_email = 'test{}@example.com'.format(self._get_long())
        url = '/admin/auth/user/{}/'.format(self.user1.pk)
        resp = self.client.post(url, {
            'username': new_email,
            'email': new_email,
            'last_login_0': self.user1.last_login.strftime('%F'),
            'last_login_1': self.user1.last_login.strftime('%T'),
            'date_joined_0': self.user1.date_joined.strftime('%F'),
            'date_joined_1': self.user1.date_joined.strftime('%T'),
        })
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(User.objects.filter(email=new_email).count(), 1)

    def test_delete_user(self):
        "test we can delete a new user using the admin"
        user = User.objects.create_user('t@e.com', 't@e.com', 'pwd')
        org_user_count = User.objects.count()
        url = '/admin/auth/user/{}/delete/'.format(user.pk)
        resp = self.client.post(url, {'post': 'yes'})
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(User.objects.count(), org_user_count - 1)
