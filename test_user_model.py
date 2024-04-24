"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Set up the test client and sample data."""
        # Set up the Flask app context
        self.app = app
        self.app_context = self.app.app_context()
        self.app_context.push()

        # Create the tables
        db.create_all()

        # Create test users
        self.u1 = User.signup("test1", "test1@example.com", "password", None)
        self.u2 = User.signup("test2", "test2@example.com", "password", None)
        db.session.commit()

    def tearDown(self):
        """Clean up after each test."""
        # Rollback the session and remove it
        db.session.rollback()
        db.session.remove()

        # Drop all tables
        db.drop_all()

        # Pop the Flask app context
        self.app_context.pop()

    def test_user_model(self):
        """Test basic user model functionality."""
        user = User.query.get(self.u1.id)
        self.assertEqual(user.username, "test1")
        self.assertEqual(user.email, "test1@example.com")
        self.assertTrue(user.password.startswith("$2b$"))

    def test_user_follows(self):
        """Test user follows functionality."""
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.following), 1)
        self.assertTrue(self.u1.is_following(self.u2))
        self.assertTrue(self.u2.is_followed_by(self.u1))

    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    ####
    #
    # Signup Tests
    #
    ####
    def test_valid_signup(self):
        u_test = User.signup("testtesttest", "testtest@test.com", "password", None)
        uid = 99999
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "testtesttest")
        self.assertEqual(u_test.email, "testtest@test.com")
        self.assertNotEqual(u_test.password, "password")
        # Bcrypt strings should start with $2b$
        self.assertTrue(u_test.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid = User.signup(None, "test@test.com", "password", None)
        uid = 123456789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid = User.signup("testtest", None, "password", None)
        uid = 123789
        invalid.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    
    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", "", None)
        
        with self.assertRaises(ValueError) as context:
            User.signup("testtest", "email@email.com", None, None)
    
    ####
    #
    # Authentication Tests
    #
    ####
    def test_valid_authentication(self):
        u = User.authenticate(self.u1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.u1.id)
    
    def test_invalid_username(self):
        self.assertFalse(User.authenticate("badusername", "password"))

    def test_wrong_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "badpassword"))