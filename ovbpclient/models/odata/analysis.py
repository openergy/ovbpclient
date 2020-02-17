from ..base import ActiveBaseModel


class Analysis(ActiveBaseModel):
    def reset(self, partial_instant=None):
        data = dict(name="reset")

        if partial_instant is not None:
            data["partial_instant"] = partial_instant

        self.client.rest_client.detail_action(
            self.endpoint,
            self.id,
            "post",
            "action",
            data=data
        )

    def get_analysis_config(self):
        if self.analysis_config is None:
            return None
        if not isinstance(self.analysis_config, dict):
            self.reload()
        return self.client.analysis_configs.data_to_record(self.analysis_config)

    def list_all_analysis_inputs(self):
        return self.client.analysis_inputs.list_all(filter_by=dict(analysis=self.id))

    def list_all_analysis_outputs(self):
        return self.client.analysis_outputs.list_all(filter_by=dict(analysis=self.id))
