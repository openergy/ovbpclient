from ..base import BaseModel
from ftputil import FTPHost
import ftputil.session


class GateFtpAccount(BaseModel):
    def attach_new_oftp_account(self):
        data = self.client.rest_client.detail_action(
            self.endpoint.path,
            self.id,
            "POST",
            "attach_new_oftp_account"
        )
        self.data = data

    def get_password(self):
        return self.client.rest_client.detail_action(
            self.endpoint.path,
            self.id,
            "get",
            "password"
        )["password"]

    def get_ftputil_client(self):
        if self.protocol == "sftp":
            raise TypeError("ftputil does not manage sftp protocol, please use another ftp client")
        if self.host == "":
            raise ValueError("ftp account is not configured, can't initialize ftputil client")
        password = self.get_password()
        session_factory = ftputil.session.session_factory(port=self.port)
        return FTPHost(
            self.host,
            self.login,
            password,
            session_factory=session_factory
        )
