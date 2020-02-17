from ..base import ActiveBaseModel


class Importer(ActiveBaseModel):
    def run(self):
        self.client.detail_action(
            self.endpoint,
            self.id,
            "post",
            "action",
            data=dict(name="run")
        )

    def reset(self, partial_instant=None, last_imported_path=None):
        if last_imported_path is not None:
            self.client.partial_update(
                self.endpoint,
                self.id,
                data=dict(last_imported_path="last_imported_path")
            )
        data = dict(name="reset")

        if partial_instant is not None:
            data["partial_instant"] = partial_instant

        self.client.detail_action(
            self.endpoint,
            self.id,
            "post",
            "action",
            data=data
        )
