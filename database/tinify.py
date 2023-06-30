import json
from base64 import b64encode

import requests

HOST = "https://api.tinify.com"
PATH_TINIFY = HOST + "/shrink"
AUTHORIZATION = "Kwdc46c3x3nyr9VbqFk2v85lXpKsWDhZ"


class Tinify(object):
    run = None

    def __init__(self):
        self.run = requests.Session()
        self.run.auth = ("api", AUTHORIZATION)

    def basic_auth(self):
        token = b64encode(f"api:{AUTHORIZATION}".encode('utf-8')).decode("ascii")
        return f'Basic {token}'

    def headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': self.basic_auth()
        }

    def post_image(self, url):
        data = {
            "source": {
                "url": url
            }
        }

        return self.run.post(PATH_TINIFY, data=json.dumps(data), headers=self.headers())

    def get_image(self, url):
        data = {
            "convert": {"type": "image/webp"}
        }
        return self.run.post(url, data=json.dumps(data), headers=self.headers())
