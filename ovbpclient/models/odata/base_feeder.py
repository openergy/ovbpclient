from ..base import BaseModel
from ..mixin_active import ActiveModelMixin


class BaseFeeder(BaseModel, ActiveModelMixin):
    def feed(self):
        self.client.detail_action(
            self.endpoint,
            self.id,
            "post",
            "feed"
        )
