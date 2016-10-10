from .outil.requests import RESTClient

_clients = {}


class Client(RESTClient):
    def __init__(self, login, password, host, port=443):
        super().__init__(
            host,
            port,
            credentials=(login, password),
            root_endpoint="api/v1"
        )

    def _check_is_on_request(self):
        return self.list("opmeasures/projects")


def set_client(login, password, host, port=443):
    global _clients
    _clients["__default__"] = Client(login, password, host, port=port)


def get_client(client=None):
    global _clients
    if client is None:
        default_client = _clients.get("__default__")
    else:
        default_client = client

    assert isinstance(default_client, RESTClient), "client must be set (and be a RESTClient object)"

    return default_client
