from openergy import get_client, get_odata_url

from . import Organization


class Project:

    @classmethod
    def retrieve(cls, organization_name=None, name=None, id=None, odata=None):
        client = get_client()
        if id is None:
            if odata is None:
                if (organization_name is None) or (name is None):
                    raise ValueError("Please indicate at least an id or an organization name and a project name "
                                     "so that the project can be retrieved")
                else:

                    r = client.list(
                        "/oteams/projects/",
                        params={
                            "name": name,
                            "organization": Organization.retrieve(organization_name).id
                        }
                    )["data"]

                    if len(r) == 0:
                        return
                    elif len(r) == 1:
                        id = r[0]["id"]
            else:
                r = client.list(
                    "/oteams/projects/",
                    params={
                        "odata": odata
                    }
                )["data"]

            if len(r) == 0:
                return
            elif len(r) == 1:
                id = r[0]["id"]

        info = client.retrieve(
            "oteams/projects",
            id
        )

        return cls(info)


    def __init__(self, info):

        if ("id" in info.keys()) and ("name" in info.keys()):
            self._info = info
            self.__dict__.update(info)
        else:
            raise ValueError("The info must contain at least 'id' and 'name' field")

    def get_detailed_info(self):

        client = get_client()

        info = client.retrieve(
            "oteams/projects",
            self.id
        )

        self._info = info
        self.__dict__.update(info)

        return self._info

    def get_organization(self):
        return Organization.retrieve(self.organization["id"])

    def delete(self):

        client = get_client()

        name = self.name

        client.destroy(
            "oteams/projects",
            self.id
        )

        for k in self._info.keys():
            setattr(self, k, None)

        self._info = None

        print(f"The project {name} has been successfully deleted")

    def _get_resource_classes(self, generators_only=False):

        # Touchy imports
        from . import Gate, Importer, Cleaner, Analysis

        classes = {
            "importer": Importer,
            "cleaner": Cleaner,
            "analysis": Analysis
        }
        if not generators_only:
            classes["gate"] = Gate

        return classes

    def get_all_resources(self, generators_only=False):

        client = get_client()

        resource_classes = self._get_resource_classes(generators_only)

        resources = []

        for resource_model, resource_class  in resource_classes.items():
            r = client.list(
                get_odata_url(resource_model),
                params={
                    "project": self.odata
                }
            )["data"]

            resources += [resource_class(info) for info in r]

        return resources

    def get_resource(self, model, name):

        resource_classes = self._get_resource_classes()

        client = get_client()
        r = client.list(
            get_odata_url(model),
            params={
                "name": name,
                "project": self.odata
            }
        )["data"]

        if len(r) == 0:
            return None
        else:
            return resource_classes[model](r[0])

    def create_internal_gate(
        self,
        name,
        timezone,
        crontab,
        script,
        comment="",
        replace=False,
        activate=True,
        passive=False
    ):

        # Touchy imports
        from . import Gate

        client = get_client()

        #verify if it exists already
        g = self.get_resource("gate", name)
        if g is not None:
            print(f"Gate {name} already existed")
            if not replace:
                return
            else:
                print(f"Deleting current gate {name}")
                g.delete()

        print(f"Creation of new gate {name}")

        gate_info = client.create(
            get_odata_url("gate"),
            data={
                "project": self.odata,
                "name": name,
                "comment": comment
            }
        )

        print(f"The gate {name} has been successfully created")

        gate = Gate(gate_info)

        gate.create_oftp_account()

        if not passive:

            base_feeder = gate.create_base_feeder(timezone, crontab)

            base_feeder.create_generic_basic_feeder(script)

            if activate:
                base_feeder.activate()
                print(f"The gate {name} has been successfully activated")

        return gate

    def create_external_gate(
            self,
            name,
            host,
            port,
            protocol,
            login,
            password,
            comment="",
            replace=False
    ):

        from . import Gate

        client = get_client()

        # verify if it exists already
        g = self.get_resource("gate", name)
        if g is not None:
            print(f"Gate {name} already existed")
            if not replace:
                return
            else:
                print(f"Deleting current gate {name}")
                g.delete()

        print(f"Creation of new gate {name}")

        gate_info = client.create(
            get_odata_url("gate"),
            data={
                "project": self.odata,
                "name": name,
                "comment": comment
            }
        )

        gate = Gate(gate_info)

        gate.update_external_ftp(
            host,
            port,
            protocol,
            login,
            password,
        )

        print(f"The gate {name} has been successfully created")

        return gate

    def create_importer(
            self,
            name,
            gate_name,
            parse_script,
            root_dir_path="/",
            crontab="",
            re_run_last_file=False,
            comment="",
            activate=True,
            replace=False,
            waiting_for_outputs=False,
            outputs_length=0,
            sleep_loop_time=15,
            abort_time=180
    ):
        """
        Parameters
        ----------

        importer_name: string
            The name of the importer

        gate_name: string
            The name of the gate to read files in

        parse_script: string
            The full python script to parse the files

        root_dir_path: string
            The path the importer starts to read files

        crontab: string
            6 characters to set the execution frequency of the importer
            (see https://platform.openergy.fr/docs/glossaire.html?highlight=crontab#crontab)

        re_run_last_file: boolean, default False
            Decides if the last file should be re-read by the importer at the beginning of each execution

        importer_comment: string, defaut ""
            An optional comment for the importer

        activate: boolean, default True
            True -> The importer get activated after creation

        replace: boolean, default False
            True -> If an importer with the same name already exists, it gets deleted and a new one get created
            False ->  If an importer with the same name already exists, a message informs you and nothing get created

        wait_for_outputs: boolean, default False
            True -> Wait for the outputs to be created. (With activate=True only)

        outputs_length: int
            The number of expected outputs.

        Returns
        -------

        The created importer instance
        """

        # Touchy import
        from . import Importer

        client = get_client()

        # verify if it exists already
        i = self.get_resource("importer", name)
        if i is not None:
            print(f"Importer {name} already existed")
            if not replace:
                return
            else:
                print(f"Deleting current importer {name}")
                i.delete()

        print(f"Creation of importer {name}")

        importer_info = client.create(
            "/odata/importers/",
            data={
                "project": self.odata,
                "name": name,
                "comment": comment
            }
        )

        importer = Importer(importer_info)

        importer.update(
            gate_name=gate_name,
            root_dir_path=root_dir_path,
            crontab=crontab,
            parse_script=parse_script,
            re_run_last_file=re_run_last_file,
            activate=False
        )

        print(f"The importer {name} has been successfully created")

        if activate:
            importer.activate()
            print(f"The importer {name} has been successfully activated")

            if waiting_for_outputs and outputs_length>0:
                importer.wait_for_outputs(outputs_length, sleep_loop_time, abort_time)

        return importer

    def create_analysis(
            self,
            name,
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
            comment="",
            activate=True,
            replace=False
    ):
        """
        Parameters
        ----------

        name: string
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

        comment: string, defaut ""
            An optional comment for the analysis

        activate: boolean, default True
            True -> The analysis get activated after creation

        replace: boolean, default False
            True -> If an analysis with the same name already exists, it gets deleted and a new one get created
            False ->  If an analysis with the same name already exists, a message informs you and nothing get created


        Returns
        -------

        The analysis record that has been created
        """

        #Touchy import
        from . import Analysis

        client = get_client()

        # verify if it exists already
        a = self.get_resource("analysis", name)
        if a is not None:
            print(f"Analysis {name} already existed")
            if not replace:
                return
            else:
                print(f"Deleting current analysis {name}")
                a.delete()

        print(f"Creation of analysis {name}")

        analysis_info = client.create(
            "odata/analyses",
            data={
                "project": self.odata,
                "name": name,
                "comment": comment
            }
        )

        analysis = Analysis(analysis_info)

        # inputs
        for input_se in inputs_list:
            input_config = inputs_config_fct(input_se)
            input_config["analysis"] = analysis.id
            client.create(
                "odata/analysis_inputs",
                data=input_config
            )

        # config

        client.create(
            "odata/analysis_configs",
            data={
                "analysis": analysis.id,
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
            output_config["analysis"] = analysis.id
            client.create(
                "odata/analysis_outputs",
                data=output_config
            )

        print(f"The analysis {name} has been successfully created")

        if activate:
            analysis.activate()
            print(f"The analysis {name} has been successfully activated")

        return analysis