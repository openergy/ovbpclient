from ..base import BaseModel
from ..mixin_active import ActiveModelMixin
from .mixin_generator import GeneratorModelMixin


class Importer(BaseModel, ActiveModelMixin, GeneratorModelMixin):
    @property
    def _tasks_endpoint(self):
        return self.client.importer_tasks
    
    def configure(
            self,
            gate=None,
            crontab=None,
            auto_partial_reset=None,
            parse_script=None,
            root_dir_path=None,
            re_run_last_file=None,
            notify_missing_files_nb=None,
            max_ante_scanned_files_nb=None
    ):
        if gate is not None:
            gate = gate.id
        data = dict()
        for k in (
            "gate",
            "crontab",
            "auto_partial_reset",
            "parse_script",
            "root_dir_path",
            "re_run_last_file",
            "notify_missing_files_nb",
            "max_ante_scanned_files_nb"
        ):
            v = locals()[k]
            if v is not None:
                data[k] = v
        self.update(**data)

    def run(self):
        rep_data = self.detail_action(
            "post",
            "action",
            data=dict(name="run")
        )
        return self.client.importer_tasks.data_to_record(rep_data)

    def reset(self, partial_instant=None, last_imported_path=None):
        if last_imported_path is not None:
            self.update(last_imported_path="last_imported_path")
        data = dict(name="reset")

        if partial_instant is not None:
            data["partial_instant"] = partial_instant

        rep_data = self.detail_action(
            "post",
            "action",
            data=data
        )
        return self.client.importer_tasks.data_to_record(rep_data)
