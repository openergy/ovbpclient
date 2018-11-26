from openergy import get_client
from . import Generator


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
        """
        Parameters
        ----------

        name: string
            The name of the importer

        comment: string

        gate_name: string
            The name of the gate to read files in
            Modifying the gate causes a reset of the importer outputs

        parse_script: string
            The full python script to parse the files
            Modifying the gate causes a reset of the importer outputs



        crontab: string
            6 characters to set the execution frequency of the importer
            (see https://platform.openergy.fr/docs/glossaire.html?highlight=crontab#crontab)

        re_run_last_file: boolean, default False
            Decides if the last file should be re-read by the importer at the beginning of each execution

        activate: boolean, default True
            True -> The importer get activated after update

        wait_for_outputs: boolean, default False
            True -> Wait for the outputs to be created. (With activate=True only)

        outputs_length: int
            The number of expected outputs.

        Returns
        -------

        An Importer instance
        """

        client = get_client()

        # deactivate before update
        self.deactivate()

        config_params = {}

        if gate_name is not None:

            # touchy import
            from . import Gate

            config_params["gate"] = Gate.retrieve(
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

                if waiting_for_outputs and (outputs_length>0):
                    self.wait_for_outputs(outputs_length)

        self.get_detailed_info()

        print(f"Importer {self.name} has been successfully updated")
