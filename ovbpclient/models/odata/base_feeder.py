from ..base import ActiveBaseModel


class BaseFeeder(ActiveBaseModel):
    def feed(self):
        self.client.detail_action(
            self.endpoint,
            self.id,
            "post",
            "feed"
        )
