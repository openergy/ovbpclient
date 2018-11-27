from openergy import get_client, get_full_list
from . import Generator, ActivationMixin


class Cleaner(Generator):

    def __init__(self, info):
        super().__init__(info)
        self.model = "cleaner"

    def delete(self):
        print("Impossible to delete a cleaner")

    def configure_all(
        self,
        unitcleaners_config_fct,
        activate=True,
        replace=False,
        waiting_for_outputs=False,
        outputs_length=0
    ):
        """
        Parameters
        ----------

        unitcleaners_config_fct: fct
            This function takes one input series resource as argument.
            You have to code this function so that it returns the configuration depending on each series
            As input of the function, you get the external name of a serie and you have to return configure_unitcleaner(**args)

        activate: boolean, default True
            True -> The unticleaners get activated after creation

        replace: boolean, default False
            True -> If a unitcleaner with the same name already exists, it gets deleted and a new one get created
            False ->  If a unitcleaner with the same name already exists, a message informs you and nothing get created

        Returns
        -------

        The configured cleaner record as a dictionary
        """

        client = get_client()

        print(f"Configuration of cleaner {self.name}")

        # retrieve unitcleaners


        importer_series = get_full_list(
            "/odata/importer_series/",
            params={"generator": self.related_importer}
        )

        # configure unitcleaners
        for se in importer_series:

            if se["unitcleaner"] is not None and replace:
                client.destroy(
                    "/odata/unitcleaners/",
                    se["unitcleaner"]
                )
            elif se["unitcleaner"] is not None and not replace:
                print(f"Unitcleaner for series {se['external_name']} already exists")
                continue

            external_name = se["external_name"]
            unitcleaner_config = unitcleaners_config_fct(external_name)

            if not isinstance(unitcleaner_config, dict):
                print(f"{se['external_name']} not configured")
                continue

            print(f'Configuration of {se["external_name"]}')

            unitcleaner_config["cleaner"] = self.id
            unitcleaner_config["external_name"] = se["external_name"]
            if unitcleaner_config["name"] is None:
                unitcleaner_config["name"] = se["external_name"]

            uc_info = client.create(
                "/odata/unitcleaners/",
                data=unitcleaner_config
            )

            if activate:
                print(f'Activation of {se["external_name"]}')
                uc = Unitcleaner(uc_info)
                uc.activate()

        if waiting_for_outputs and (outputs_length>0):
            self.wait_for_outputs(outputs_length)

        self.get_detailed_info()

        print(f"The cleaner {self.name} has successfully been configured")

    def clear_all_configurations(self):

        client = get_client()

        # retrieve unitcleaners
        importer_series = get_full_list(
            "/odata/importer_series/",
            params={"generator": self.related_importer}
        )

        # destroy all
        for se in importer_series:
            if se["unitcleaner"] is not None:
                client.destroy(
                    "/odata/unitcleaners/",
                    se["unitcleaner"]
                )

        print(f"{len(importer_series)} configurations cleared")

    def clear_one_configuration(self, external_name):

        client = get_client()

        se = self.get_importer_series_from_external_name(external_name)

        if se["unitcleaner"] is not None:
            client.destroy(
                "/odata/unitcleaners/",
                se["unitcleaner"]
            )
            print(f"{se['external_name']} configuration successfully cleared")
        else:
            print(f"{se['external_name']} not configured")

    def get_importer_series_from_external_name(
            self,
            external_name
    ):
        """

        Parameters
        ----------
        external_name: string

        Returns
        -------
        A Series instance.

        """

        client = get_client()

        importer_series = client.list(
            "/odata/importer_series/",
            params={
                "generator": self.related_importer,
                "external_name": external_name
            }
        )["data"]

        if len(importer_series) == 0:
            print(f"No input series named {external_name} found in the cleaner {self.name}")
            return
        elif len(importer_series) == 1:
            return importer_series[0]

    def configure_one(
            self,
            external_name,
            name=None,
            freq="1H",
            input_unit_type="instantaneous",
            unit_type="instantaneous",
            input_convention="left",
            clock="tzt",
            timezone="Europe/Paris",
            unit=None,
            resample_rule="mean",
            interpolate_limit=None,
            wait_offset="6H",
            label=None,
            input_expected_regular=None,
            operation_fct=None,
            filter_fct=None,
            derivative_filter_fct=None,
            custom_delay=None,
            custom_fct=None,
            custom_before_offset=None,
            custom_after_offset=None,
            activate=True,
    ):

        client = get_client()

        importer_series = self.get_importer_series_from_external_name(external_name)

        if importer_series is not None:

            data = configure_unitcleaner(
                external_name if name is None else name,
                freq,
                input_unit_type,
                unit_type,
                input_convention,
                clock,
                timezone,
                unit,
                resample_rule,
                interpolate_limit,
                wait_offset,
                label,
                input_expected_regular,
                operation_fct,
                filter_fct,
                derivative_filter_fct,
                custom_delay,
                custom_fct,
                custom_before_offset,
                custom_after_offset
            )

            uc_info = client.create(
                "/odata/unitcleaners/",
                data=data
            )

            print(f'Unitcleaner {external_name} configured.')

            uc = Unitcleaner(uc_info)

            if activate:
                uc.activate()
                print(f'Unitcleaner {external_name} activated.')

            return uc

    def get_unitcleaners(self):

        unitcleaners = get_full_list(
            "/odata/unitcleaners/",
            params={"cleaner": self.id}
        )

        if len(unitcleaners) > 0:
            return[Unitcleaner(uc) for uc in unitcleaners]
        else:
            print(f"Cleaner {self.name} has no unitcleaners")
            return

    def activate(self):
        unitcleaners = self.get_unitcleaners()
        if unitcleaners is not None:
            for uc in unitcleaners:
                if not uc.active:
                    uc.activate()

    def deactivate(self):
        unitcleaners = self.get_unitcleaners()
        if unitcleaners is not None:
            for uc in unitcleaners:
                if uc.active:
                    uc.deactivate()


class Unitcleaner(ActivationMixin):

    def __init__(self, info):
        self._info = info
        self.__dict__.update(info)

        self.activable_object_model = "unitcleaner"
        self.activable_object_id = self.id


def configure_unitcleaner(
        name = None,
        freq = "1H",
        input_unit_type = "instantaneous",
        unit_type = "instantaneous",
        input_convention = "left",
        clock = "tzt",
        timezone = "Europe/Paris",
        unit=None,
        resample_rule="mean",
        interpolate_limit=None,
        wait_offset="6H",
        label=None,
        input_expected_regular=None,
        operation_fct=None,
        filter_fct=None,
        derivative_filter_fct=None,
        custom_delay=None,
        custom_fct=None,
        custom_before_offset=None,
        custom_after_offset=None
):
    '''

    Parameters
    ----------
        name: string, default None
    The name of the cleaned series. If None, the external_name is unsed

    for the following params, see platform documentation at "https://platform.openergy.fr/docs/"

    freq
    input_unit_type
    unit_type
    input_convention
    clock
    timezone
    unit
    resample_rule
    interpolate_limit
    wait_offset
    label
    input_expected_regular
    operation_fct
    filter_fct
    derivative_filter_fct
    custom_delay
    custom_fct
    custom_before_offset
    custom_after_offset

    Returns
    -------
    Request params for unitcleaner configuration
    '''

    data = {
        "name": name,
        "freq": freq,
        "input_unit_type": input_unit_type,
        "unit_type": unit_type,
        "input_convention": input_convention,
        "clock": clock,
        "timezone": timezone,
        "resample_rule": resample_rule,
        "wait_offset": wait_offset,
        "custom_delay": custom_delay
    }

    if unit is not None:
        data["unit"] = unit
    if interpolate_limit is not None:
        data["interpolate_limit"] = interpolate_limit
    if label is not None:
        data["label"] = label
    if input_expected_regular is not None:
        data["input_expected_regular"] = input_expected_regular,
    if operation_fct is not None:
        data["operation_fct"] = operation_fct,
    if filter_fct is not None:
        data["filter_fct"] = filter_fct,
    if derivative_filter_fct is not None:
        data["derivative_filter_fct"] = derivative_filter_fct,
    if custom_delay is not None:
        data["custom_delay"] = custom_delay,
    if custom_fct is not None:
        data["custom_delay"] = custom_fct,
    if custom_before_offset is not None:
        data["custom_before_offset"] = custom_before_offset,
    if custom_after_offset is not None:
        data["custom_after_offset"] = custom_after_offset,

    return data
