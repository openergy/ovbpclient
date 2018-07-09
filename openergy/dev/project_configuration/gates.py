from openergy import get_client

from . import Resource, ActivationMixin


class Gate(Resource):

    model = "gate"

    def create_oftp_account(self):

        client = get_client()

        client.detail_route(
            "odata/gate_ftp_account",
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

        print("base_feeder_info", base_feeder_info)

        return BaseFeeder(base_feeder_info)

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