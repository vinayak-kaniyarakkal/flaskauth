import unittest
import os
import json
from pathlib import Path


TEST_DB_PATH = 'testdb.sqlite3'


class WidgetTestCase(unittest.TestCase):
    def setUp(self):
        os.environ['IS_TEST'] = 'True'
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass
        Path(TEST_DB_PATH).touch()
        os.system('sqlite3 testdb.sqlite3 < migrations\\00_initial.sql')
        self.setup_app()
        res = self.client.post(
            '/register',
            data={'name': 'vinayak', 'password': 'vinayak@123'},
            follow_redirects=True,
        )

    def setup_app(self):
        import app
        self.client = app.app.test_client()
        self.app = app

    def test_success(self):
        res = self.client.post(
            '/login',
            data={'username': 'vinayak', 'password': 'vinayak@123'},
            follow_redirects=True,
        )
        try:
            token = json.loads(next(res.response))['token']
        except:
            self.fail('Did not get token for valid login')
        try:
            log_obj = self.app.ValidLogin.query.order_by(self.app.ValidLogin.time.desc()).first()
        except Exception as e:
            print(e)
            self.fail('Log not created for valid login')
        if not self.app.User.query.filter_by(id=log_obj.user_id).first():
            self.fail('Log not created for valid login')

    def test_fail(self):
        res = self.client.post(
            '/login',
            data={'username': 'vinayak', 'password': 'wrong!!!'},
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 401, msg='Expected 401 when wrong password given')
        try:
            log_obj = self.app.InvalidLogin.query.order_by(self.app.InvalidLogin.time.desc()).first()
        except Exception as e:
            print(e)
            self.fail('Log not created for invalid login')
        self.assertEqual(log_obj.name, 'vinayak', 'Log not created for invalid login')
        

if __name__ == "__main__":
    unittest.main()
