from ..base import BaseModel


class Project(BaseModel):
    # mail alerts
    def activate_mail_alerts(self):
        return self.update(mail_alerts_activated=True)

    def deactivate_mail_alerts(self):
        return self.update(mail_alerts_activated=False)
