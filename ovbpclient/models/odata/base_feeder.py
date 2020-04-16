from ..base import BaseModel
from ..mixin_active import ActiveModelMixin


class BaseFeeder(BaseModel, ActiveModelMixin):
    def feed(self):
        rep_data = self.client.detail_action(
            self.endpoint,
            self.id,
            "post",
            "feed"
        )
        return self.client.base_feeder_tasks.data_to_record(rep_data)
