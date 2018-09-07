from openergy import get_client

from . import Resource, ActivationMixin


class Gate(Resource):

    def __init__(self, info):
        super().__init__(info)
        self.model = "gate"
        self._password = None

    def create_oftp_account(self):

        client = get_client()

        client.detail_route(
            "odata/gate_ftp_accounts",
            self.ftp_account,
            "POST",
            "attach_new_oftp_account",
            data={}
        )

    def create_base_feeder(self, timezone, crontab):
        client = get_client()

        base_feeder_info = client.create(
            "odata/base_feeders",
            data={
                "gate": self.id,
                "timezone": timezone,
                "crontab": crontab
            }
        )

        return BaseFeeder(base_feeder_info)

    def get_base_feeder(self):
        self.get_detailed_info()
        if self._info["base_feeder"] is not None:
            return BaseFeeder(self._info["base_feeder"])
        else:
            print(f"Gate {self._info['name']} has no base_feeder")
            return

    def deactivate(self):
        base_feeder = self.get_base_feeder()
        if base_feeder is not None:
            base_feeder.deactivate()

    def activate(self):
        base_feeder = self.get_base_feeder()
        if base_feeder is not None:
            base_feeder.activate()

    def update_external_ftp(
        self,
        host,
        port,
        protocol,
        login,
        password
    ):

        client = get_client()

        client.partial_update(
            "odata/gate_ftp_accounts",
            self.ftp_account,
            data={
                "custom_host": host,
                "custom_port": port,
                "custom_protocol": protocol,
                "custom_login": login,
                "password": password
            }
        )

        return self.get_detailed_info()

    def list_dir(self, path="/"):
        client = get_client()

        return client.list(
            f"odata/gate_ftp_accounts/{self.ftp_account['id']}/list_dir/",
            params={"path": path}
        )["data"]

    def check_last_files(self, path="/"):
        dir_list = self.list_dir(path)
        files_list = [d["name"] for d in dir_list if d["type"]=="file"]
        files_list.sort(reverse=True)
        return files_list

    @property
    def ftp_account_password(self):

        client = get_client()

        self._password = client.detail_route(
            "odata/gate_ftp_accounts",
            self.ftp_account['id'],
            "GET",
            "password"
        )["password"]

        return self._password


class BaseFeeder(ActivationMixin):

    def __init__(self, info):
        self._info = info
        self.__dict__.update(info)

        self.activable_object_model = "base_feeder"
        self.activable_object_id = self.id

    def create_generic_basic_feeder(self, script):

        client = get_client()

        generic_basic_feeder_info = client.create(
            "odata/generic_basic_feeders",
            data={
                "base_feeder": self.id,
                "script": script
            }
        )

        return GenericBasicFeeder(generic_basic_feeder_info)


class GenericBasicFeeder():

    def __init__(self, info):
        self._info = info
        self.__dict__.update(info)