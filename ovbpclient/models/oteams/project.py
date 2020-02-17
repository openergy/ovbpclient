from ..base import BaseModel


class Project(BaseModel):
    def _create_record(self, endpoint, name, comment=None):
        data = dict(name=name, project=self.data)
        if comment is not None:
            data[comment] = comment
        return endpoint.create(data)

    def _get_record_by_name(self, endpoint, name):
        # todo: check that my filter_by works
        records = endpoint.list(limit=2, filter_by=dict(name=name, project=self.get_odata_project().id))
        return records.one()

    def _list_all(self, endpoint, other_filters=None):
        filter_by = dict(project=self.get_odata_project().id)
        if other_filters:
            filter_by.update(other_filters)
        return endpoint.list_all(filter_by=filter_by)

    # odata projects
    def get_odata_project(self):
        data = self.odata if isinstance(self.odata, dict) else dict(id=self.odata)
        return self.client.odata_projects.data_to_record(data)

    # gates
    def create_gate(self, name, comment=None):
        return self._create_record(self.client.gates, name, comment=comment)

    def get_gate_by_name(self, name):
        return self._get_record_by_name(self.client.gates, name)

    def list_all_gates(self):
        return self._list_all(self.client.gates)

    # importers
    def create_importer(self, name, comment=None):
        return self._create_record(self.client.importers, name, comment=comment)

    def get_importer_by_name(self, name):
        return self._get_record_by_name(self.client.importers, name)

    def list_all_importers(self):
        return self._list_all(self.client.importers)

    # cleaners
    def create_cleaner(self, name, comment=None):
        return self._create_record(self.client.cleaners, name, comment=comment)

    def get_cleaner_by_name(self, name):
        return self._get_record_by_name(self.client.cleaners, name)

    def list_all_cleaners(self):
        return self._list_all(self.client.cleaners)

    # analyses
    def create_analysis(self, name, comment=None):
        return self._create_record(self.client.analyses, name, comment=comment)

    def get_analysis_by_name(self, name):
        return self._get_record_by_name(self.client.analyses, name)

    def list_all_analyses(self):
        return self._list_all(self.client.analyses)

    # notifications
    def list_all_notifications(self, resolved=None):
        other_filters = None if resolved is None else dict(resolved=resolved)
        return self._list_all(self.client.notifications, other_filters=other_filters)
