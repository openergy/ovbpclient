from .resources_general import get_resource_from_name, activate_resource, waiting_for_outputs

def configure_cleaner(
        client,
        project,
        cleaner_name,
        unitcleaner_config_fct,
        activate=True,
        replace=False,
        wait_for_outputs=False
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: dictionary
        Project record

    cleaner_name: string
        The name of the cleaner

    unitcleaner_config_fct: fct
        This function takes one input series resource as argument.
        You have to code this function so that it returns the configuration depending on each series

    activate: boolean, default True
        True -> The unticleaners get activated after creation

    replace: boolean, default False
        True -> If a unitcleaner with the same name already exists, it gets deleted and a new one get created
        False ->  If a unitcleaner with the same name already exists, a message informs you and nothing get created

    wait_for_outputs: boolean, default False
        True -> Wait for the outputs to be created. (With activate=True only)

    Returns
    -------

    The configured cleaner record as a dictionary
    """

    cleaner = get_resource_from_name(client, project, cleaner_name, "cleaner")

    if cleaner is None:
        return

    # retrieve unitcleaners
    importer_series = client.list(
        "/odata/importer_series/",
        params={"generator": cleaner["related_importer"]}
    )["data"]

    # configure unitcleaners
    for se in importer_series:

        if se["unitcleaner"] is not None and replace:
            client.destroy(
                "/odata/unitcleaners/",
                se["unitcleaner"]
            )
        elif se["unitcleaner"] is not None and not replace:
            print(f"Unitcleaner for series {se['external_name']} already exists")

        unitcleaner_config = unitcleaner_config_fct(se)
        unitcleaner_config["cleaner"] = cleaner["id"]

        uc = client.create(
            "/odata/unitcleaners/",
            data=unitcleaner_config
        )

        print(f'{se["external_name"]} configured.')

        if activate:
            activate_resource(client, uc, "unitcleaner")

    if wait_for_outputs:
        waiting_for_outputs(client, cleaner, "cleaner", len(importer_series))

    return cleaner

def get_unitcleaner_config(
        cleaner,
        external_name,
        name,
        freq,
        input_unit_type,
        unit_type,
        input_convention,
        clock,
        timezone,
        unit=None,
        resample_rule=None,
        interpolate_limit=None,
):
    data = {
        "cleaner": cleaner["id"],
        "external_name": external_name,
        "name": name,
        "freq": freq,
        "input_unit_type": input_unit_type,
        "unit_type": unit_type,
        "input_convention": input_convention,
        "clock": clock,
        "timezone": timezone,
    }

    if unit is not None:
        data["unit"] = unit
    if resample_rule is not None:
        data["resample_rule"] = resample_rule
    if interpolate_limit is not None:
        data["interpolate_limit"] = interpolate_limit

    return data


def get_importer_series_from_external_name(
        client,
        cleaner,
        external_name
):

    importer_series = client.list(
        "/odata/importer_series/",
        params={
            "generator": cleaner["related_importer"],
            "external_name": external_name
        }
    )["data"]

    if len(importer_series) == 0:
        print(f"No input series named {external_name} found for the cleaner {cleaner['name']}")
    elif len(importer_series) == 1:
        return importer_series[0]
    else:
        print(f"Several input series named {external_name} found for the cleaner {cleaner['name']}")

    return


def create_unitcleaner(
        client,
        cleaner,
        external_name,
        name,
        freq,
        input_unit_type,
        unit_type,
        input_convention,
        clock,
        timezone,
        unit=None,
        resample_rule=None,
        interpolate_limit=None,
        activate=True
):

    importer_series = get_importer_series_from_external_name(
        client,
        cleaner,
        external_name
    )

    if importer_series is not None:

        data = {
            "cleaner": cleaner["id"],
            "external_name": external_name,
            "name": name,
            "freq": freq,
            "input_unit_type": input_unit_type,
            "unit_type": unit_type,
            "input_convention": input_convention,
            "clock": clock,
            "timezone": timezone,
        }

        if unit is not None:
            data["unit"] = unit
        if resample_rule is not None:
            data["resample_rule"] = resample_rule
        if interpolate_limit is not None:
            data["interpolate_limit"] = interpolate_limit

        uc = client.create(
            "/odata/unitcleaners/",
            data=data
        )

        print(f'Unitcleaner {external_name} configured.')

        if activate:
            activate_resource(client, uc, "unitcleaner")

        return uc