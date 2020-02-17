from ..base import BaseModel


class GateFtpAccount(BaseModel):
    def attach_new_oftp_account(self):
        data = self.client.rest_client.detail_action(
            "odata/gate_ftp_accounts",
            self.id,
            "POST",
            "attach_new_oftp_account"
        )
        self.data = data

    def get_password(self):
        return self.client.detail_action(
            self.endpoint,
            self.id,
            "get",
            "password"
        )["password"]
