from openergy import get_client
from . import Generator, ActivationMixin


class Cleaner(Generator):

    def __init__(self, info):
        super().__init__(info)
        self.model = "cleaner"

    def activate(self):
        return

    def deactivate(self):
        return

    def delete(self):
        print("Impossible to delete a cleaner")

    def configure_all(
            self,
            unitcleaner_config_fct,
            activate=True,
            replace=False,
            waiting_for_outputs=False,
            outputs_length=0
    ):
        """
        Parameters
        ----------

        unitcleaner_config_fct: fct
            This function takes one input series resource as argument.
            You have to code this function so that it returns the configuration depending on each series

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

        # retrieve unitcleaners
        importer_series = client.list(
            "/odata/importer_series/",
            params={"generator": self.related_importer}
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
                continue

            unitcleaner_config = unitcleaner_config_fct(se)
            unitcleaner_config["cleaner"] = self.id

            uc_info = client.create(
                "/odata/unitcleaners/",
                data=unitcleaner_config
            )

            print(f'{se["external_name"]} configured.')

            if activate:
                uc = Unitcleaner(uc_info)
                uc.activate()
                print(f'{se["external_name"]} activated.')

                if waiting_for_outputs:
                    self.wait_for_outputs(outputs_length)

        return self.get_detailed_info()

    def get_importer_series_from_external_name(
            self,
            external_name
    ):

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

        client = get_client()

        importer_series = self.get_importer_series_from_external_name(external_name)

        if importer_series is not None:

            data = {
                "cleaner": self.id,
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

            uc_info = client.create(
                "/odata/unitcleaners/",
                data=data
            )

            print(f'Unitcleaner {external_name} configured.')

            if activate:
                uc = Unitcleaner(uc_info)
                uc.activate()
                print(f'Unitcleaner {external_name} activated.')

            return uc_info


class Unitcleaner(ActivationMixin):

    def __init__(self, info):
        self._info = info
        self.__dict__.update(info)

        self.activable_object_model = "unitcleaner"
        self.activable_object_id = self.id


def get_unitcleaner_config(
        external_name,
        name,
        freq,
        input_unit_type,
        unit_type,
        input_convention,
        clock,
        timezone,
        wait_offset="6H",
        unit=None,
        resample_rule=None,
        interpolate_limit=None,
        custom_delay=None
):
    data = {
        "external_name": external_name,
        "name": name,
        "freq": freq,
        "input_unit_type": input_unit_type,
        "unit_type": unit_type,
        "input_convention": input_convention,
        "clock": clock,
        "timezone": timezone,
        "wait_offset": wait_offset,
        "custom_delay": custom_delay
    }

    if unit is not None:
        data["unit"] = unit
    if resample_rule is not None:
        data["resample_rule"] = resample_rule
    if interpolate_limit is not None:
        data["interpolate_limit"] = interpolate_limit

    return data