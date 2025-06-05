import base64
import random
import threading
import time
import unittest

import requests

from rickle.net import serve_rickle_http
from rickle import Rickle
from twisted.internet import reactor

expected_data = {
        'app': {
            'version': '1.0.0',
            'username' : 'john'
        }
    }

port_number = random.randint(8082,8088)


class TestBasicAuth(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.thread = threading.Thread(target=serve_rickle_http,
                                  kwargs={
                                      'rickle': Rickle(expected_data),
                                      'port': port_number,
                                      'interface': '',
                                      'serialised': False,
                                      'output_type': 'JSON',
                                      'basic_auth': {'larry': 'ken sent m3'},
                                      'threaded': True
                                  }
                                  )
        cls.thread.start()
        time.sleep(1)  # Give time for reactor to start

    @classmethod
    def tearDownClass(cls):
        def stop():
            reactor.stop()

        reactor.callFromThread(stop)
        cls.thread.join()


    def test_get_endpoint(self):
        headers = {'Authorization': f"Basic {base64.b64encode('larry:ken sent m3'.encode()).decode()}"}

        response = requests.get(f'http://localhost:{port_number}/', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data)

        response = requests.get(f'http://localhost:{port_number}/app', headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_data['app'])

        response = requests.get(f'http://localhost:{port_number}/not_found', headers=headers)
        self.assertEqual(response.status_code, 404)




if __name__ == "__main__":
    unittest.main()