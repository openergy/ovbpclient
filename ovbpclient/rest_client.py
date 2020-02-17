import time
import requests

from .exceptions import HttpError
from .json import json_loads


def check_rep(rep):
    if (rep.status_code // 100) != 2:
        raise HttpError(rep.text, rep.status_code)


def rep_to_json(rep):
    # we use our json loads for date parsing
    return json_loads(rep.text)


class RestClient:
    MAX_ITERATIONS = 100

    def __init__(
            self,
            host,
            credentials=None,
            port=443,
            verify_ssl=True
    ):
        """
        credentials: login, password
        """
        if "http" not in host:
            host = "http://%s" % host

        self.base_url = "%s:%s" % (host, port)
        self.session = requests.Session()
        if credentials is not None:
            self.session.auth = credentials
        self.verify_ssl = verify_ssl

    def list(self, endpoint, params=None):
        rep = self.session.get(
            f"{self.base_url}/{endpoint}/",
            params=params,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def retrieve(self, endpoint, resource_id):
        rep = self.session.get(
            f"{self.base_url}/{endpoint}/{resource_id}/",
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def create(self, plural_rel, data):
        rep = self.session.post(
            f"{self.base_url}/{plural_rel}",
            json=data,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def partial_update(self, endpoint, resource_id, data):
        rep = self.session.patch(
            f"{self.base_url}/{endpoint}/{resource_id}",
            json=data,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def update(self, endpoint, resource_id, data):
        rep = self.session.put(
            f"{self.base_url}/{endpoint}/{resource_id}",
            json=data,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def detail_action(
            self, 
            endpoint,
            resource_id,
            http_method, 
            action_name, 
            params=None,
            data=None, 
            return_json=True,
            send_json=True):
        rep = getattr(self.session, http_method.lower())(
            f"{self.base_url}/{endpoint}/{resource_id}/{action_name}",
            params=params,
            json=data if send_json else None,
            data=None if send_json else data,
            verify=self.verify_ssl
        )
        if rep.status_code == 204:
            return

        if return_json:
            return rep_to_json(rep)
        check_rep(rep)
        return rep.content

    def list_action(
            self, 
            plural_rel, 
            http_method, 
            action_name, 
            params=None, 
            data=None, 
            return_json=True, 
            send_json=True):
        rep = getattr(self.session, http_method.lower())(
            f"{self.base_url}/{plural_rel}/{action_name}",
            params=params,
            json=data if send_json else None,
            data=None if send_json else data,
            verify=self.verify_ssl
        )
        if rep.status_code == 204:
            return

        if return_json:
            return rep_to_json(rep)
        check_rep(rep)
        return rep.content

    def destroy(self, endpoint, resource_id, params=None):
        rep = self.session.delete(
            f"{self.base_url}/{endpoint}/{resource_id}",
            params=params,
            verify=self.verify_ssl)
        if rep.status_code == 204:
            return
        return rep_to_json(rep)

    def wait_for_on(self, timeout=10, freq=1):
        start = time.time()
        if timeout <= 0:
            raise ValueError
        while True:
            if (time.time() - start) > timeout:
                raise TimeoutError
            try:
                rep = self.session.get(
                    f"{self.base_url}/oteams/projects/",
                    params=dict(empty=True),  # todo: check works
                    verify=self.verify_ssl)
                if rep.status_code == 503:
                    raise TimeoutError
                break
            except (requests.exceptions.ConnectionError, TimeoutError):
                pass
            time.sleep(freq)
