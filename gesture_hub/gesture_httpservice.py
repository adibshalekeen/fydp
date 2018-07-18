import http.client
import json
class http_service(object):
    def __init__(self, ip):
        print(ip)
        self.connection = http.client.HTTPSConnection(ip)
        self.response = {}
    def get(self, path):
        print(path)
        self.connection.request('GET', path)
        self.response = self.connection.getresponse()

    def post(self, path, data):
        json_data = json.dumps(data)
        self.connection.request('POST', path, json_data)
        self.response = self.connection.getresponse()
