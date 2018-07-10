from .outil.requests import RESTClient

_client = None


class Client(RESTClient):
    def __init__(self, login, password, host, port=443, verify_ssl=True):
        super().__init__(
            host,
            port,
            verify_ssl=verify_ssl,
            credentials=(login, password),
            root_endpoint="api/v2"
        )

    def _check_is_on_request(self):
        return self.list("oteams/projects")


def set_client(login, password, host, port=443, verify_ssl=True):
    global _client
    _client = Client(login, password, host, port=port, verify_ssl=verify_ssl)
    return _client


def get_client():
    global _client
    return _client
