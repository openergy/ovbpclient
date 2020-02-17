from openergy import get_client, get_full_list
from . import Generator


class Analysis(Generator):

    def __init__(self, info):
        super().__init__(info)

        # from Resource
        self.model = "analysis"

        # from ActivationMixin
        self.activable_object_model = "analysis"
        self.activable_object_id = self.id

    def update(
            self,
            name=None,
            inputs_list=None,
            inputs_config_fct=None,
            output_names_list=None,
            outputs_config_fct=None,
            input_freq=None,
            output_freq=None,
            clock=None,
            output_timezone=None,
            script=None,
            start_with_first=None,
            wait_for_last=None,
            before_offset_strict_mode=None,
            custom_before_offset=None,
            custom_after_offset=None,
            custom_delay=None,
            wait_offset=None,
            comment=None,
            activate=True,
            waiting_for_outputs=False,
            outputs_lentgh = 0
    ):

        client = get_client()

        self.deactivate()

        settings_params = {}

        if name is not None:
            settings_params["name"] = name
        if comment is not None:
            settings_params["comment"] = comment

        if len(settings_params.keys())>0:
            client.partial_update(
                "odata/analyses",
                self.id,
                data=settings_params
            )

        # inputs
        if inputs_list is not None:

            # delete old inputs
            old_inputs = get_full_list(
                "odata/analysis_inputs",
                params={
                    "analysis": self.id
                }
            )

            for input in old_inputs:
                client.destroy(
                    "odata/analysis_inputs",
                    input["id"]
                )

            # create new ones
            for input_se in inputs_list:
                input_config = inputs_config_fct(input_se)
                input_config["analysis"] = self.id
                client.create(
                    "odata/analysis_inputs",
                    data=input_config
                )

        # config
        config_params={}

        if input_freq is not None:
            config_params["input_freq"] = input_freq
        if output_freq is not None:
            config_params["output_freq"] = output_freq
        if clock is not None:
            config_params["clock"] = clock
        if output_timezone is not None:
            config_params["output_timezone"] = output_timezone
        if script is not None:
            config_params["script"] = script
        if start_with_first is not None:
            config_params["start_with_first"] = start_with_first
        if wait_for_last is not None:
            config_params["wait_for_last"] = wait_for_last
        if before_offset_strict_mode is not None:
            config_params["before_offset_strict_mode"] = before_offset_strict_mode
        if custom_before_offset is not None:
            config_params["custom_before_offset"] = custom_before_offset
        if custom_after_offset is not None:
            config_params["custom_after_offset"] = custom_after_offset
        if custom_delay is not None:
            config_params["custom_delay"] = custom_delay
        if wait_offset is not None:
            config_params["wait_offset"] = wait_offset

        if len(config_params.keys())>0:

            analysis_config = client.list(
                "odata/analysis_configs",
                params={
                    "analysis": self.id
                }
            )["data"][0]

            client.partial_update(
                "odata/analysis_configs",
                analysis_config["id"],
                data= config_params
            )

        # outputs
        if output_names_list is not None:
            # delete old inputs
            old_outputs = get_full_list(
                "odata/analysis_outputs",
                params={
                    "analysis": self.id
                }
            )["data"]

            for output in old_outputs:
                client.destroy(
                    "odata/analysis_outputs",
                    output["id"]
                )

            # create new ones
            for output_name in output_names_list:
                output_config = outputs_config_fct(output_name)
                output_config["analysis"] = self.id
                client.create(
                    "odata/analysis_outputs",
                    data=output_config
                )

        print(f"The analysis {self.name} has been successfully updated")

        if activate:
            self.activate()

            if waiting_for_outputs and (outputs_lentgh>0):
                self.wait_for_outputs(outputs_lentgh)

        self.get_detailed_info()

    def reset(
            self,
            partial_instant=None,
            waiting_for_outputs=False,
            outputs_lentgh = 0
    ):
        """
        Parameters
        ----------

        partial_instant: string (date in iso format) default None
            The date from which the outputs are reset.
            If None, full reset.

        waiting_for_outputs

        """

        client = get_client()

        data = {"name": "reset"}

        if partial_instant is not None:
            data["partial_instant"] = partial_instant

        client.detail_action(
            "odata/analyses",
            self.id,
            "POST",
            "action",
            data=data
        )

        if waiting_for_outputs and (outputs_lentgh > 0):
            self.wait_for_outputs(outputs_lentgh)


def get_analysis_input_config(
        input_series_name,
        column_name,
        input_series_generator
):

    return {
        "input_series_name": input_series_name,
        "column_name": column_name,
        "input_series_generator": input_series_generator
    }


def get_analysis_output_config(
        name,
        unit="",
        resample_rule="mean"
):

    return {
        "name": name,
        "unit": unit,
        "resample_rule": resample_rule
    }