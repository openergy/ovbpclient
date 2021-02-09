import ovbpclient
from ..base import BaseModel


class Gate(BaseModel):
    def attach_internal_ftp_account(self):
        ftp_account = self.client.gate_ftp_accounts.data_to_record({"id": self.ftp_account})
        return ftp_account.attach_internal_ftp_account()

    def create_base_feeder(self, timezone=None, crontab=None):
        data = dict(gate=self.id)
        if timezone is not None:
            data["timezone"] = timezone
        if crontab is not None:
            data["crontab"] = crontab
        return self.client.base_feeders.create(**data)

    def get_base_feeder(self) -> "ovbpclient.models.odata.BaseFeeder":
        if self.base_feeder is None:
            return None
        if not isinstance(self.base_feeder, dict):
            self.reload()
        return self.client.base_feeders.data_to_record(self.base_feeder)

    def get_ftp_account(self) -> "ovbpclient.models.odata.GateFtpAccount":
        return self.client.gate_ftp_accounts.data_to_record(self.ftp_account)

    def get_ftputil_client(self):
        return self.get_ftp_account().get_ftputil_client()

    def run(self):
        base_feeder = self.get_base_feeder()
        if base_feeder is None:
            raise RuntimeError("no base_feeder attached to gate, can't run")
        base_feeder.feed()

    def activate(self):
        base_feeder = self.get_base_feeder()
        if base_feeder is None:
            raise RuntimeError("no base_feeder attached to gate, can't activate")
        base_feeder.activate()

    def deactivate(self):
        base_feeder = self.get_base_feeder()
        if base_feeder is None:
            return
        base_feeder.deactivate()
