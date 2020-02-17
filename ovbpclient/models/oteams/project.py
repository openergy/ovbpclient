from ..base import BaseModel


class Project(BaseModel):
    def _create_record(self, endpoint, name, comment=None):
        data = dict(name=name, project=self.id)
        if comment is not None:
            data[comment] = comment
        return endpoint.create(data)

    def _get_record_by_name(self, endpoint, name):
        # todo: check that my filter_by works
        records = endpoint.list(limit=2, filter_by=dict(name=name, project=self.id))
        return records.one()

    def create_gate(self, name, comment=None):
        return self._create_record(self.client.gates, name, comment=comment)

    def get_gate_by_name(self, name):
        return self._get_record_by_name(self.client.gates, name)

    def create_importer(self, name, comment=None):
        return self._create_record(self.client.importers, name, comment=comment)

    def get_importer_by_name(self, name):
        return self._get_record_by_name(self.client.importers, name)

    def create_cleaner(self, name, comment=None):
        return self._create_record(self.client.cleaners, name, comment=comment)

    def get_cleaner_by_name(self, name):
        return self._get_record_by_name(self.client.cleaners, name)

    def create_analysis(self, name, comment=None):
        return self._create_record(self.client.analyses, name, comment=comment)

    def get_analysis_by_name(self, name):
        return self._get_record_by_name(self.client.analyses, name)

    def list_all_notifications(self, resolved=None):
        filter_by = dict(project=self.id)
        if resolved is not None:
            filter_by["resolved"] = resolved
        return self.client.notifications.list_all(filter_by=filter_by)
