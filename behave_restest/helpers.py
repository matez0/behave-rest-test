import requests


class Request(requests.Request):
    def __init__(self, *args, endpoint, **kwargs):
        super().__init__(*args, **kwargs)
        self.endpoint = endpoint

    def send(self, base_url):
        self.url = base_url + self.endpoint

        prepared_request = self.prepare()

        with requests.Session() as session:
            return session.send(prepared_request)
