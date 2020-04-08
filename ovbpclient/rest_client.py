import time
import requests

from .exceptions import HttpError
from .json import json_loads


def check_rep(rep):
    if (rep.status_code // 100) != 2:
        raise HttpError(rep.text, rep.status_code)


def rep_to_json(rep):
    check_rep(rep)
    # we use our json loads for date parsing
    return json_loads(rep.text)


class RestClient:
    MAX_ITERATIONS = 100

    def __init__(
            self,
            url,
            login,
            password,
            verify_ssl=True
    ):
        self.base_url = url.strip("/")
        self.session = requests.Session()
        self.session.auth = (login, password)
        self.verify_ssl = verify_ssl

    def list(self, path, params=None):
        rep = self.session.get(
            f"{self.base_url}/{path}/",
            params=params,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def retrieve(self, path, resource_id):
        rep = self.session.get(
            f"{self.base_url}/{path}/{resource_id}/",
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def create(self, path, data):
        rep = self.session.post(
            f"{self.base_url}/{path}",
            json=data,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def partial_update(self, path, resource_id, data):
        rep = self.session.patch(
            f"{self.base_url}/{path}/{resource_id}",
            json=data,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def update(self, path, resource_id, data):
        rep = self.session.put(
            f"{self.base_url}/{path}/{resource_id}",
            json=data,
            verify=self.verify_ssl)
        return rep_to_json(rep)

    def detail_action(
            self, 
            path,
            resource_id,
            http_method, 
            action_name, 
            params=None,
            data=None, 
            return_json=True,
            send_json=True):
        rep = getattr(self.session, http_method.lower())(
            f"{self.base_url}/{path}/{resource_id}/{action_name}",
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
            path,
            http_method, 
            action_name, 
            params=None, 
            data=None, 
            return_json=True, 
            send_json=True):
        rep = getattr(self.session, http_method.lower())(
            f"{self.base_url}/{path}/{action_name}",
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

    def destroy(self, path, resource_id, params=None):
        rep = self.session.delete(
            f"{self.base_url}/{path}/{resource_id}",
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
                    params=dict(empty=True),
                    verify=self.verify_ssl)
                if rep.status_code == 503:
                    raise TimeoutError
                break
            except (requests.exceptions.ConnectionError, TimeoutError):
                pass
            time.sleep(freq)
