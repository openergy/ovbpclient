from .resources_general import resource_already_exists, activate_resource, waiting_for_outputs, deactivate_resource, \
    delete_resource


def create_analysis(
        client,
        project,
        analysis_name,
        inputs_list,
        inputs_config_fct,
        output_names_list,
        outputs_config_fct,
        input_freq,
        output_freq,
        clock,
        output_timezone,
        script,
        start_with_first=False,
        wait_for_last=False,
        before_offset_strict_mode=False,
        custom_before_offset=None,
        custom_after_offset=None,
        custom_delay=None,
        wait_offset='6H',
        analysis_comment="",
        activate=True,
        replace=False,
        wait_for_outputs=False
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: string
        The project record

    analysis_name: string
        The name of the analysis

    inputs_list: list of series resources
        The script loops through this list to create the analysis_inputs according to the following function

    inputs_config_fct: function
        This function takes a series resource as argument and returns the associated input config

    output_names_list: list
        The list of the output names. You can't retrieve it from a test for the moment.
        The script loops through this list to create the analysis_outputs according to the following function

    outputs_config_fct: function
        This function takes the name of the output as argument and returns the associated output config

    input_freq: string (pandas freq format)
        The freq of the input dataframe

    output_freq: string (pandas freq format)
        the freq of the output dataframe

    clock: ["gmt", "dst", "tzt"]
        the clock of the output dataframe

    output_timezone: string
        the timezone of the output dataframe

    script: string
        the full analysis script

    start_with_first: boolean
        start analysis with first data ignoring custom offsets

    wait_for_last: boolean
        wait for all series to have data to launch analysis

    before_offset_strict_mode: boolean
        don't start analysis until the custom_before_offset is reached

    custom_before_offset: string (pandas freq format)
        the quantity of data before time t to compute the value at time t

    custom_after_offset: string (pandas freq format)
        the quantity of data after time t to compute the value at time t

    custom_delay: string (pandas freq format)

    wait_offset: string (pandas freq format)

    analysis_comment: string, defaut ""
        An optional comment for the analysis

    activate: boolean, default True
        True -> The analysis get activated after creation

    replace: boolean, default False
        True -> If an analysis with the same name already exists, it gets deleted and a new one get created
        False ->  If an analysis with the same name already exists, a message informs you and nothing get created

    wait_for_outputs: boolean, default False
        True -> Wait for the outputs to be created. (With activate=True only)


    Returns
    -------

    The analysis record that has been created
    """

    if resource_already_exists(client, project, analysis_name, "analysis", replace):
        return

    print(f"Creation of analysis {analysis_name}")

    analysis = client.create(
        "odata/analyses",
        data={
            "project": project["odata"],
            "name": analysis_name,
            "comment": analysis_comment
        }
    )

    # inputs
    for input_se in inputs_list:
        input_config = inputs_config_fct(input_se)
        input_config["analysis"] = analysis["id"]
        client.create(
            "odata/analysis_inputs",
            data=input_config
        )

    # config

    client.create(
        "odata/analysis_configs",
        data={
            "analysis": analysis["id"],
            # Basic
            "script_method": 'array',
            "input_freq": input_freq,
            "output_freq": output_freq,
            "clock": clock,
            "output_timezone": output_timezone,
            "script": script,

            # Expert
            "start_with_first": start_with_first,
            "wait_for_last": wait_for_last,
            "before_offset_strict_mode": before_offset_strict_mode,
            "custom_before_offset": custom_before_offset,
            "custom_after_offset": custom_after_offset,

            # Outputs
            "custom_delay": custom_delay,
            "wait_offset": wait_offset
        }
    )

    # outputs
    for output_name in output_names_list:
        output_config = outputs_config_fct(output_name)
        output_config["analysis"] = analysis["id"]
        client.create(
            "odata/analysis_outputs",
            data=output_config
        )

    print(f"The analysis {analysis_name} has been successfully created")

    if activate:
        activate_resource(client, analysis, "analysis")

        if wait_for_outputs:
            waiting_for_outputs(client, analysis, "analysis", len(output_names_list))

    return analysis


def update_analysis(
        client,
        analysis,
        analysis_name=None,
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
        analysis_comment=None,
        activate=True,
        wait_for_outputs=False
):

    if analysis["active"]:
        deactivate_resource(
            client,
            analysis,
            "analysis"
        )

    settings_params = {}

    if analysis_name is not None:
        settings_params["name"] = analysis_name
    if analysis_comment is not None:
        settings_params["comment"] = analysis_comment

    if len(settings_params.keys())>0:
        client.partial_update(
            "odata/analyses",
            analysis["id"],
            data=settings_params
        )

    # inputs
    if inputs_list is not None:
        # delete old inputs
        old_inputs = client.list(
            "odata/analysis_inputs",
            params={
                "analysis": analysis["id"]
            }
        )["data"]

        for input in old_inputs:
            delete_resource(
                client,
                input,
                "analysis_input"
            )

        # create new ones
        for input_se in inputs_list:
            input_config = inputs_config_fct(input_se)
            input_config["analysis"] = analysis["id"]
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
                "analysis": analysis["id"]
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
        old_outputs = client.list(
            "odata/analysis_outputs",
            params={
                "analysis": analysis["id"]
            }
        )["data"]

        for output in old_outputs:
            delete_resource(
                client,
                output,
                "analysis_output"
            )

        # create new ones
        for output_name in output_names_list:
            output_config = outputs_config_fct(output_name)
            output_config["analysis"] = analysis["id"]
            client.create(
                "odata/analysis_outputs",
                data=output_config
            )

    print(f"The analysis {analysis['name']} has been successfully updated")

    if activate:
        activate_resource(client, analysis, "analysis")

        if wait_for_outputs:
            waiting_for_outputs(client, analysis, "analysis", len(output_names_list))

    return analysis


def reset_analysis(
        client,
        analysis,
        partial_instant=None
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    analysis: Analysis resource as a dictionary

    partial_instant: string (date in iso format) default None
        The date from which the outputs are reset.
        If None, full reset.

    """

    data = {"value": "reset"}

    if partial_instant is not None:
        data["partial_instant"] = partial_instant

    client.detail_route(
        "odata/analyses",
        analysis["id"],
        "POST",
        "action",
        data=data
    )


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