from ..base import BaseModel
from ..mixin_active import ActiveModelMixin


class BaseFeeder(BaseModel, ActiveModelMixin):
    def get_child(self):
        if self.child_id is None:
            return None
        if self.child_model == "genericbasicfeeder":
            return self.client.generic_basic_feeders.retrieve(self.child_id)
        if self.child_model == "staticwebservicefeeder":
            return self.client.static_webservice_feeders.retrieve(self.child_id)
        raise RuntimeError(f"Unknown child model: {self.child_model}, please report this bug.")

    def feed(self):
        rep_data = self.client.detail_action(
            self.endpoint,
            self.id,
            "post",
            "feed"
        )
        return self.client.base_feeder_tasks.data_to_record(rep_data)
