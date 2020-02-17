import time
import datetime as dt
from collections import OrderedDict
import pandas as pd
import numpy as np

from openergy import get_client, get_odata_url, get_full_list
from . import Resource, ActivationMixin


class Generator(Resource, ActivationMixin):

    def __init__(self, info):
        super().__init__(info)
        self.model = None
        self.activable_object_model = None
        self.activable_object_id = None

    def get_outputs(self):

        # Touchy import
        from . import Series

        client = get_client()

        r = get_full_list(
            "odata/series",
            params={
                "generator":self.id
            }
        )

        return [Series(info) for info in r]

    def wait_for_outputs(
        self,
        outputs_length,
        sleep_loop_time=15,
        abort_time=180
    ):

        client = get_client()

        outputs_ready = False
        start_time = dt.datetime.now()

        while not outputs_ready:

            if (dt.datetime.now() - start_time) < dt.timedelta(seconds=abort_time):

                print('Waiting for outputs...')
                time.sleep(sleep_loop_time)

                outputs = self.get_outputs()

                print(f"{len(outputs)} outputs generated over {outputs_length} expected")

                if len(outputs) == outputs_length:
                    print(f"Outputs are ready \n\n")
                    return

            else:
                print("Abort time exceeded. Exit")
                return

    def delete(self, time_limit=5*60*60):

        client = get_client()

        self.deactivate()

        outputs = self.get_outputs()

        if len(outputs) == 0:

            name = self.name
            model = self.model

            client.destroy(
                get_odata_url(self.model),
                self.id
            )

            for k in self._info.keys():
                setattr(self, k, None)

            self._info = None

            print(f"The {model} {name} has been successfully deleted")

        else:

            too_long = False
            print(f"Clearing outputs before deleting")

            clear = client.detail_action(
                get_odata_url(self.model),
                self.id,
                "POST",
                "action",
                data={"name": "clear"}
            )

            clear_task_status = "pending"
            clear_start = dt.datetime.now()

            end_status = ["finished", "failed", "server_error", "refused"]

            while clear_task_status not in end_status and not too_long:
                now = dt.datetime.now()
                if (now - clear_start) > dt.timedelta(seconds=time_limit):
                    too_long = True
                    print("Clear operation took too long. Aborting deletion")
                    continue

                time.sleep(10)
                clear_task = client.retrieve(
                    get_odata_url(f"{self.model}_task"),
                    clear["id"],
                )

                clear_task_status = clear_task["base"]["status"]
                print(f"Clear status : {clear_task_status}")

            if not too_long:

                name = self.name

                client.destroy(
                    get_odata_url(self.model),
                    self.id
                )

                for k in self._info.keys():
                    setattr(self, k, None)

                self._info = None

                print(f"The {self.model} {name} has been successfully deleted")

    def data_scan(self):
        outputs = self.get_outputs()
        df_data = OrderedDict({
            "Organization": self.get_organization().name,
            "Project": self.get_project().name,
            "Generator Model": self.model,
            "Generator Name": self.name,
            "Series Name": [],
            "Series Start": [],
            "Series End" : [],
            "Timestep": [],
            "Points Last Day": [],
            "Points Last Week": []
        })
        for out in outputs:
            df_data["Series Name"] += [out.name]
            df_data["Timestep"] += [out.freq]

            if out.start is not None:
                df_data["Series Start"] += [out.start]
                df_data["Series End"] += [out.end]
                df_data["Points Last Week"] += \
                    [out.get_data(start=dt.datetime.now() - dt.timedelta(days=7)).notnull().sum()]
                df_data["Points Last Day"] += \
                    [out.get_data(start=dt.datetime.now() - dt.timedelta(days=1)).notnull().sum()]
            else:
                df_data["Series Start"] += [np.datetime64('NaT')]
                df_data["Series End"] += [np.datetime64('NaT')]
                df_data["Points Last Week"] += [0]
                df_data["Points Last Day"] += [0]

        return pd.DataFrame(df_data)
