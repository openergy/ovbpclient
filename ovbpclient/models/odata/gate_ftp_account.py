from .ftp_account import FtpAccount


class GateFtpAccount(FtpAccount):
    def attach_new_oftp_account(self):
        data = self.detail_action(
            "POST",
            "attach_new_oftp_account"
        )
        self.data = data
