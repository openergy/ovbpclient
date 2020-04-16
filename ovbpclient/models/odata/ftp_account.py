from ..base import BaseModel
from .ftp_entry import FtpEntry

from ftputil import FTPHost
import ftputil.session


class FtpAccount(BaseModel):
    def get_password(self):
        return self.detail_action(
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

    def list_dir(
            self,
            path="/",
            root_dir_path="/",
            start=0,
            limit=200
    ):
        rep_data = self.detail_action(
            "post",
            "list_dir",
            params=dict(start=start, length=limit),
            data=dict(path=path, root_dir_path=root_dir_path)
        )
        return [FtpEntry(**data) for data in rep_data["data"]]
