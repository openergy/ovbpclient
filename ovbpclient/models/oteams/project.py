from ovbpclient.models import odata as odata_models
from typing import List
from ..base import BaseModel
from ...util import get_one_and_only_one


class Project(BaseModel):
    def _create_record(self, endpoint, name, comment=""):
        return endpoint.create(project=self.odata_id, name=name, comment=comment)

    def _get_record_by_name(self, endpoint, name):
        records = endpoint.list(limit=2, filter_by=dict(name=name, project=self.get_odata_project().id))
        return get_one_and_only_one(records)

    def _list_all(self, endpoint, other_filters=None):
        filter_by = dict(project=self.get_odata_project().id)
        if other_filters:
            filter_by.update(other_filters)
        return endpoint.list_all(filter_by=filter_by)

    # odata projects
    @property
    def odata_id(self):
        return self.odata["id"] if isinstance(self.odata, dict) else self.odata

    def get_odata_project(self):
        data = self.odata if isinstance(self.odata, dict) else dict(id=self.odata)
        return self.client.odata_projects.data_to_record(data)

    # gates
    def create_gate(self, name, comment="") -> "odata_models.Gate":
        return self._create_record(self.client.gates, name, comment=comment)

    def get_gate(self, name) -> "odata_models.Gate":
        return self._get_record_by_name(self.client.gates, name)

    def list_all_gates(self) -> List["odata_models.Gate"]:
        return self._list_all(self.client.gates)

    # importers
    def create_importer(self, name, comment="") -> "odata_models.Importer":
        return self._create_record(self.client.importers, name, comment=comment)

    def get_importer(self, name) -> "odata_models.Importer":
        return self._get_record_by_name(self.client.importers, name)

    def list_all_importers(self) -> List["odata_models.Importer"]:
        return self._list_all(self.client.importers)

    # cleaners
    def create_cleaner(self, name, comment="") -> "odata_models.Cleaner":
        return self._create_record(self.client.cleaners, name, comment=comment)

    def get_cleaner(self, name) -> "odata_models.Cleaner":
        return self._get_record_by_name(self.client.cleaners, name)

    def list_all_cleaners(self) -> List["odata_models.Cleaner"]:
        return self._list_all(self.client.cleaners)

    # analyses
    def create_analysis(self, name, comment="") -> "odata_models.Analysis":
        return self._create_record(self.client.analyses, name, comment=comment)

    def get_analysis(self, name) -> "odata_models.Analysis":
        return self._get_record_by_name(self.client.analyses, name)

    def list_all_analyses(self) -> List["odata_models.Analysis"]:
        return self._list_all(self.client.analyses)

    # series
    def list_all_series(self) -> List["odata_models.Series"]:
        return self._list_all(self.client.series)

    # notifications
    def list_all_notifications(self, resolved=None) -> List["odata_models.Notification"]:
        other_filters = None if resolved is None else dict(resolved=resolved)
        return self._list_all(self.client.notifications, other_filters=other_filters)
