from ..base import BaseModel


class User(BaseModel):
    @property
    def odata_id(self):
        return self.odata["id"] if isinstance(self.odata, dict) else self.odata

    def get_odata_user(self):
        data = self.odata if isinstance(self.odata, dict) else dict(id=self.odata)
        odata_user = self.client.odata_users.data_to_record(data)
        odata_user.reload()
        return odata_user

    def get_odata_ftp_account(self):
        odata_user = self.get_odata_user()
        ftp_account_id = odata_user.ftp_account["id"] if isinstance(odata_user.ftp_account, dict) \
            else odata_user.ftp_account
        ftp_account = self.client.user_ftp_accounts.data_to_record(dict(id=ftp_account_id))
        ftp_account.reload()
        return ftp_account
