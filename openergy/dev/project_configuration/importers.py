import datetime as dt
import time

from openergy import get_client, get_full_list
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
            last_imported_path=None,
            activate=True,
            waiting_for_outputs=False,
            outputs_length=0,
            waiting_for_cleaner_inputs=False
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

            gate = Gate.retrieve(
                self.get_organization().name,
                self.get_project().name,
                gate_name
            )

            config_params["gate"] = gate.id
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

                if waiting_for_outputs and (outputs_length>0) and (len(gate.list_dir())>0):
                    self.wait_for_outputs(outputs_length)

                    if waiting_for_cleaner_inputs:
                        self.wait_for_cleaner_inputs(outputs_length)

        self.get_detailed_info()

        print(f"Importer {self.name} has been successfully updated")

    def run(self):

         client = get_client()

         client.detail_route(
             "odata/importers",
             self.id,
             "POST",
             "action",
             data={"name":"run"}
         )

    def reset(
            self,
            partial_instant=None,
            last_imported_path=None,
            waiting_for_outputs=False,
            outputs_lentgh = 0,
            waiting_for_cleaner_inputs=False
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

        if last_imported_path is not None:
            client.partial_update(
                "odata/importers",
                self.id,
                data={"last_imported_path": last_imported_path}
            )

        data = {"name": "reset"}

        if partial_instant is not None:
            data["partial_instant"] = partial_instant

        client.detail_route(
            "odata/importers",
            self.id,
            "POST",
            "action",
            data=data
        )

        if waiting_for_outputs and (outputs_lentgh > 0):
            self.wait_for_outputs(outputs_lentgh)

            if waiting_for_cleaner_inputs:
                self.wait_for_cleaner_inputs(outputs_lentgh)

    def wait_for_cleaner_inputs(
        self,
        outputs_length,
        sleep_loop_time=15,
        abort_time=180
    ):

        client = get_client()

        cleaner_inputs_ready = False
        start_time = dt.datetime.now()

        while not cleaner_inputs_ready:

            if (dt.datetime.now() - start_time) < dt.timedelta(seconds=abort_time):

                print('Waiting for cleaner inputs...')
                time.sleep(sleep_loop_time)

                importer_series = get_full_list(
                    "/odata/importer_series/",
                    params={"generator": self.id}
                )

                print(f"{len(importer_series)} cleaner inputs generated over {outputs_length} expected")

                if len(importer_series) == outputs_length:
                    print(f"Cleaner inputs are ready \n\n")
                    return

            else:
                print("Abort time exceeded. Exit")
                return
