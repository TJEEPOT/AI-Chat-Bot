import unittest
from io import BytesIO
from context import presenter


class MyTestCase(unittest.TestCase):
    def setUp(self):  # executed prior to each test
        presenter.app.config['TESTING'] = True
        presenter.app.config['WTF_CSRF_ENABLED'] = False
        presenter.app.config['DEBUG'] = False
        # presenter.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(presenter.app.config[
        # 'BASEDIR'], db)
        self.app = presenter.app.test_client()

    def tearDown(self):  # executed after each test
        pass

    def test_home(self):
        response = self.app.get("/", follow_redirects=True)
        self.assertEqual(200, response.status_code)

    def test_get_audio(self):
        with open(r"data/test_1.wav", "rb") as rec1:
            audio = rec1.read()
        data = {'file': (BytesIO(audio), 'test.txt')}
        response = self.app.post("/get_audio", content_type="multipart/form-data", data=data, follow_redirects=True)
        self.assertEqual(200, response.status_code)
        self.assertEqual("this is a test of the voice recogniser", response.get_json().get("message"))


if __name__ == '__main__':
    unittest.main()
