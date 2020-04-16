from ..base import BaseModel
from ..mixin_active import ActiveModelMixin
from .mixin_generator import GeneratorModelMixin


class Analysis(BaseModel, ActiveModelMixin, GeneratorModelMixin):
    def run(self):
        rep_data = self.detail_action(
            "post",
            "action",
            data=dict(name="run")
        )
        return self.client.analysis_tasks.data_to_record(rep_data)

    def _partial_action(self, action, partial_instant=None):
        data = dict(name=action)

        if partial_instant is not None:
            data["partial_instant"] = partial_instant

        return self.detail_action(
            "post",
            "action",
            data=data
        )

    def clear(self, partial_instant=None):
        rep_data = self._partial_action("clear", partial_instant=partial_instant)
        return self.client.analysis_tasks.data_to_record(rep_data)

    def reset(self, partial_instant=None):
        rep_data = self._partial_action("reset", partial_instant=partial_instant)
        return self.client.analysis_tasks.data_to_record(rep_data)

    # analysis config
    def get_analysis_config(self):
        if self.analysisconfig is None:
            return None
        if not isinstance(self.analysisconfig, dict):
            self.reload()
        return self.client.analysis_configs.data_to_record(self.analysisconfig)

    def create_analysis_config(
            self,
            input_freq,
            output_freq,
            script,
            clock="tzt",
            output_timezone="Europe/Paris",
            start_with_first=False,
            wait_for_last=False,
            custom_before_offset=None,
            custom_after_offset=None,
            before_offset_strict_mode=False,
            with_tags=False,
            wait_offset="6H",
            custom_delay=None
    ):
        return self.client.analysis_configs.create(
            analysis=self.id,
            input_freq=input_freq,
            output_freq=output_freq,
            script=script,
            clock=clock,
            output_timezone=output_timezone,
            start_with_first=start_with_first,
            wait_for_last=wait_for_last,
            custom_before_offset=custom_before_offset,
            custom_after_offset=custom_after_offset,
            before_offset_strict_mode=before_offset_strict_mode,
            with_tags=with_tags,
            wait_offset=wait_offset,
            custom_delay=custom_delay,
            script_method="array"
        )

    # inputs
    def list_all_analysis_inputs(self):
        return self.client.analysis_inputs.list_all(filter_by=dict(analysis=self.id))

    def create_analysis_input(self, generator, series_name, column_name):
        return self.client.analysis_inputs.create(
            analysis=self.id,
            input_series_generator=generator.id,
            input_series_name=series_name,
            column_name=column_name
        )

    # outputs
    def list_all_analysis_outputs(self):
        return self.client.analysis_outputs.list_all(filter_by=dict(analysis=self.id))

    def create_analysis_output(self, name, resample_rule, label="", unit="", numerical_filter=None):
        return self.client.analysis_outputs.create(
            analysis=self.id,
            name=name,
            resample_rule=resample_rule,
            label=label,
            unit=unit,
            numerical_filter=numerical_filter
        )
