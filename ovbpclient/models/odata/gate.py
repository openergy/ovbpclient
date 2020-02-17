from ..base import BaseModel


class Gate(BaseModel):
    def attach_new_oftp_account(self):
        ftp_account = self.client.gate_ftp_accounts.data_to_record({"id": self.ftp_account})
        return ftp_account.attach_new_oftp_account()

    def create_base_feeder(self, timezone=None, crontab=None):
        data = dict(gate=self.id)
        if timezone is not None:
            data["timezone"] = timezone
        if crontab is not None:
            data["crontab"] = crontab
        return self.client.base_feeders.create(data)

    def get_base_feeder(self):
        if self.base_feeder is None:
            return None
        if not isinstance(self.base_feeder, dict):
            self.reload()
        return self.client.base_feeders.data_to_record(self.base_feeder)

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
