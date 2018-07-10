from openergy import get_client
from . import Generator, Resource


class Importer(Generator):

    def __init__(self, info):
        super().__init__(info)
        self.model = "importer"
        self.activable_object_model = "importer"
        self.activable_object_id = self.id

    def update(
            self,
            name=None,
            comment=None,
            gate_name=None,
            parse_script=None,
            root_dir_path=None,
            crontab=None,
            re_run_last_file=None,
            activate=True,
            waiting_for_outputs=False,
            outputs_length=0,

    ):

        client = get_client()

        # deactivate before update
        self.deactivate()

        config_params = {}

        if gate_name is not None:
            config_params["gate"] = Resource.retrieve(
                "gate",
                self.get_organization().name,
                self.get_project().name,
                gate_name
            ).id
        if parse_script is not None:
            config_params["parse_script"] = parse_script
        if root_dir_path is not None:
            config_params["root_dir_path"] = root_dir_path
        if crontab is not None:
            config_params["crontab"] = crontab
        if re_run_last_file is not None:
            config_params["re_run_last_file"] = re_run_last_file

        if name is not None:
            config_params["name"] = name
        if comment is not None:
            config_params["comment"] = comment

        if len(config_params.keys()) > 0:

            client.partial_update(
                "odata/importers",
                self.id,
                data=config_params
            )

            if activate:
                self.activate()

                if waiting_for_outputs:
                    self.wait_for_outputs(outputs_length)

        return self.get_detailed_info()