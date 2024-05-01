import unittest
from app import create_app
from models.models import db

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_register(self):
        response = self.client.post('/register', json={
            'name': 'Fulano de Tal',
            'email': ''
        })

if __name__ == '__main__':
    unittest.main()
