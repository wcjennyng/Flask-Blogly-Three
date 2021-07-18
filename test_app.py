from unittest import TestCase

from app import app
from models import db, User

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

# This is a bit of hack, but don't use Flask DebugToolbar
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']

db.drop_all()
db.create_all()

class UserTestCase(TestCase):
    """Tests User"""

    def setUp(self):
        """Add sample User"""
        User.query.delete()

        user = User(first_name='Jenny', last_name='Ng', image_url='https://image.flaticon.com/icons/png/128/1077/1077114.png')
        db.session.add(user)
        db.session.commit()

        self.user_id = user_id

    def tearDown(self):
        """Clean up any fouled transcation"""
        db.session.rollback()

    def test_users_index(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Jenny', html)

    def test_users_edit(self):
        with app.test_client() as client:
            resp = client.get(f"/users/{self.user_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Jenny</h1>', html)

    def test_new_user_form(self):
        with app.test_client() as client:
            d = {'first_name' :'Jennifer', 'last_name' : 'Ngo', 'image_url':'https://image.flaticon.com/icons/png/128/1077/1077114.png'}
            resp = client.post('/users/new_user', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("<h1>Jennifer</h1>", html)

class PostTestCase(TestCase):
    """Test Post"""

    def setUp(self):
        """Add sample Post"""
        Post.query.delete()

        post = Post(title='I love', content='CATS', created_at='Tuesday, 21. Novemeber 2006 04:30PM')
        db.session.add(post)
        db.session.commit()

        self.post_id = post_id

    def tearDown(self):
        """Clean up any fouled transcation"""
        db.session.rollback()

    def test_posts_edit(self):
        with app.test_client() as client:
            resp = client.get(f"/posts/{self.post_id}/edit")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>I love</h1>', html)


    def test_posts_show(self):
        with app.test_client() as client:
            resp = client.get(f'/posts/{self.post_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('I love', html)
