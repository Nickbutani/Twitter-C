import os
from unittest import TestCase

# Assuming models.py and app.py are configured correctly
from models import db, User, Message, Likes, Follows
from app import app, CURR_USER_KEY

# Use a separate test database
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# App configuration for testing

app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['DEBUG'] = False

# Ensure the Flask app is configured to use the test database
db.app = app


class MessageModelTestCase(TestCase):
    """Test views for messages."""

    @classmethod
    def setUpClass(cls):
        """Set up things to be run once before all tests."""
        with app.app_context():
            db.create_all()

    @classmethod
    def tearDownClass(cls):
        """Tear down things to be run once after all tests."""
        with app.app_context():
            db.drop_all()

    def setUp(self):
        """Create test client, add sample data."""
        self.client = app.test_client()

        with app.app_context():
            self.setup_data()

    def setup_data(self):
        """Set up users and other test data."""
        User.query.delete()  # Clear out any existing users
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id
        db.session.commit()

    def tearDown(self):
        """Clean up any fouled transaction."""
        with app.app_context():
            db.session.rollback()

    # Example test method
    def test_message_model(self):
        """Does basic model work?"""
        m = Message(text="Hello", user_id=self.testuser_id)
        db.session.add(m)
        db.session.commit()

        # Test that the message was inserted correctly
        self.assertEqual(len(Message.query.all()), 1)
        self.assertEqual(Message.query.first().text, "Hello")

    def test_message_likes(self):
        m1 = Message(
            text="a warble",
            user_id=self.uid
        )

        m2 = Message(
            text="a very interesting warble",
            user_id=self.uid 
        )

        u = User.signup("yetanothertest", "t@email.com", "password", None)
        uid = 888
        u.id = uid
        db.session.add_all([m1, m2, u])
        db.session.commit()

        u.likes.append(m1)

        db.session.commit()

        l = Likes.query.filter(Likes.user_id == uid).all()
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].message_id, m1.id)


        