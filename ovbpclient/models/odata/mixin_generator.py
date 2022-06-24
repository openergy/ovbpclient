import abc
from typing import List
from ovbpclient.models import odata as odata_models


class GeneratorModelMixin:
    def _partial_action(self, action, partial_instant=None):
        data = dict(name=action)

        if partial_instant is not None:
            data["partial_instant"] = partial_instant

        return self.detail_action(
            "post",
            "action",
            data=data
        )

    def list_all_output_series(self) -> List["odata_models.Series"]:
        return self.client.series.list_all(filter_by=dict(generator=self.id))

    def run(self):
        rep_data = self.detail_action(
            "post",
            "action",
            data=dict(name="run")
        )
        return self._tasks_endpoint.data_to_record(rep_data)

    def clear(self, partial_instant=None):
        rep_data = self._partial_action("clear", partial_instant=partial_instant)
        return self._tasks_endpoint.data_to_record(rep_data)

    def reset(self, partial_instant=None):
        rep_data = self._partial_action("reset", partial_instant=partial_instant)
        return self._tasks_endpoint.data_to_record(rep_data)

    # to subclass
    @property
    @abc.abstractmethod
    def _tasks_endpoint(self):
        pass
