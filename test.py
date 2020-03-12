import os
import os.path
import threading
import unittest
import json
from http.server import SimpleHTTPRequestHandler
import socketserver
from app import app
from app.api_v1_bp import get_station, add_if_not_exist
from app.configuration import normalize_db_uri
from app.models import Station, db


class MyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.test_json = {
            "id": "1",
            "name": "Москва",
            "lines": [
                {
                    "id": "8",
                    "hex_color": "FFCD1C",
                    "name": "Калининская",
                    "stations": [
                        {
                            "id": "8.189",
                            "name": "Новокосино",
                            "lat": 55.745113,
                            "lng": 37.864052,
                            "order": 0
                        },
                        {
                            "id": "8.88",
                            "name": "Новогиреево",
                            "lat": 55.752237,
                            "lng": 37.814587,
                            "order": 1
                        }
                    ]
                }
            ]
        }
        super().__init__(*args, **kwargs)

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        prepared_json = json.dumps(self.test_json)
        self.wfile.write(str.encode(prepared_json))


class ThreadedHTTPServer(object):
    handler = MyHandler

    def __init__(self, host, port):
        self.server = socketserver.TCPServer((host, port), self.handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever)
        self.server_thread.daemon = True

    def start(self):
        self.server_thread.start()

    def stop(self):
        self.server.shutdown()
        self.server.server_close()


class ApiV1TestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.testing_server = ThreadedHTTPServer("", 5001)
        cls.testing_server.start()
        app.config['TESTING'] = True
        uri_base_dir = normalize_db_uri()
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:////{uri_base_dir}test_db.sqlite3'
        app.config['METRO_STATION_URL'] = 'http://127.0.0.1:5001/'
        cls.app = app.test_client()

    def setUp(self) -> None:
        self.metro_url = 'http://127.0.0.1:5001/'
        self.get_station_output = {
            "id": "1",
            "name": "Москва",
            "lines": [
                {
                    "id": "8",
                    "hex_color": "FFCD1C",
                    "name": "Калининская",
                    "stations": [
                        {
                            "id": "8.189",
                            "name": "Новокосино",
                            "lat": 55.745113,
                            "lng": 37.864052,
                            "order": 0
                        },
                        {
                            "id": "8.88",
                            "name": "Новогиреево",
                            "lat": 55.752237,
                            "lng": 37.814587,
                            "order": 1
                        }
                    ]
                }
            ]
        }

        self.station = {
            "metro_id": "8.189",
            "name": "Новокосино",
            "lat": 55.745113,
            "lng": 37.864052,
            "order": 0
        }

        self.station_mod = {
            "metro_id": "8.189",
            "name": "Неновокосино",
            "lat": 55.745113,
            "lng": 37.864052,
            "order": 0
        }

        self.compare_url = "http://127.0.0.1:5000/api/v1/metro/verificate"
        self.compare_post_data = ["Новокосино", "new_station"]
        self.compare_post_data_r = {'deleted': ['Новогиреево'], 'unchanged': ['Новокосино'], 'updated': ['new_station']}
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    @classmethod
    def tearDownClass(cls):
        cls.testing_server.stop()
        os.remove(os.path.join(os.getcwd(), "test_db.sqlite3"))

    def test_get_station(self):
        r = get_station(self.metro_url)
        self.assertEqual(r, self.get_station_output)

    def test_add_if_not_exit(self):
        instance, new = add_if_not_exist(**self.station)
        self.assertTrue(new)
        for k, v in self.station.items():
            if k == "metro_id":
                self.assertEqual(v, str(getattr(instance, k)))
                continue
            self.assertEqual(v, getattr(instance, k))
        instance, new = add_if_not_exist(**self.station_mod)
        self.assertFalse(new)
        for k, v in self.station_mod.items():
            if k == "metro_id":
                self.assertEqual(v, str(getattr(instance, k)))
                continue
            self.assertEqual(v, getattr(instance, k))

    def test_compairer_allowed_methods(self):
        r = self.app.get(self.compare_url)
        self.assertEqual(r._status, '405 METHOD NOT ALLOWED')
        r = self.app.put(self.compare_url)
        self.assertEqual(r._status, '405 METHOD NOT ALLOWED')
        r = self.app.delete(self.compare_url)
        self.assertEqual(r._status, '405 METHOD NOT ALLOWED')
        r = self.app.patch(self.compare_url)
        self.assertEqual(r._status, '405 METHOD NOT ALLOWED')

    def test_compairer_func(self):
        r = self.app.post(self.compare_url, data=json.dumps(self.compare_post_data))
        self.assertEqual(r._status, '200 OK')
        self.assertEqual(r.get_json(), self.compare_post_data_r)


if __name__ == '__main__':
    unittest.main()
