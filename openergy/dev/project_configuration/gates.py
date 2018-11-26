from openergy import get_client, get_full_list

from . import Resource, ActivationMixin


class Gate(Resource):

    def __init__(self, info):
        super().__init__(info)
        self.model = "gate"
        self._password = None

    def create_oftp_account(self):

        client = get_client()

        client.detail_route(
            "odata/gate_ftp_accounts",
            self.ftp_account,
            "POST",
            "attach_new_oftp_account",
            data={}
        )

    def create_base_feeder(self, timezone, crontab):
        client = get_client()

        base_feeder_info = client.create(
            "odata/base_feeders",
            data={
                "gate": self.id,
                "timezone": timezone,
                "crontab": crontab
            }
        )

        return BaseFeeder(base_feeder_info)

    def get_base_feeder(self):
        self.get_detailed_info()
        if self._info["base_feeder"] is not None:
            return BaseFeeder(self._info["base_feeder"])
        else:
            print(f"Gate {self._info['name']} has no base_feeder")
            return

    def deactivate(self):
        base_feeder = self.get_base_feeder()
        if base_feeder is not None:
            base_feeder.deactivate()

    def activate(self):
        base_feeder = self.get_base_feeder()
        if base_feeder is not None:
            base_feeder.activate()

    def update_general(
        self,
        name=None,
        comment=None
    ):
        """

        Parameters
        ----------
        name: srting

        comment: string

        """

        params = {}
        args = ["name", "comment"]
        for arg in args:
            if locals()[arg] is not None:
                params[arg] = locals()[arg]

        if len(params.keys()) == 0:
            print("No modifications to apply")

        client = get_client()

        client.partial_update(
            "odata/gates",
            self.id,
            data=params
        )


    def update_internal(
        self,
        name=None,
        comment=None,
        crontab=None,
        timezone =None,
        script=None,
        activate=True,
        passive=False

    ):

        """
        Parameters
        ----------
        name: string defult None
            name of the Gate

        crontab: string default None
            6 characters to set the execution frequency of the importer
            (see https://platform.openergy.fr/docs/glossaire.html?highlight=crontab#crontab)

        script: string default None
            The feeding script

        comment: string default None
            An optional comment

        timezone: srting default None

        activate: bool default True
            activate the gate directly after creation

        passive: bool default False
            create a passive gate

        """

        if self.get_base_feeder() is None:
            print ("This gate is not internal")
            return

        general_params = ["name", "comment"]
        params = {}
        for p in general_params:
            if locals()[p] is not None:
                params[p] = locals()[p]
        if len(params) > 0:
            self.update_general(**params)

        base_feeder_params = ["crontab", "timezone"]
        params = {}
        for p in base_feeder_params:
            if locals()[p] is not None:
                params[p] = locals()[p]
        if len(params) > 0:
            base_feeder = self.get_base_feeder()
            base_feeder.update(**params)

        generic_basic_feeder_params = ["script"]
        params = {}
        for p in generic_basic_feeder_params:
            if locals()[p] is not None:
                params[p] = locals()[p]
        if len(params) > 0:
            base_feeder = self.get_base_feeder()
            generic_basic_feeder = base_feeder.get_generic_basic_feeder()
            generic_basic_feeder.update(**params)

        if activate:
            self.activate()

        self.get_detailed_info()

        print(f"The gate {self.name} has been successfully updated")

    def update_external(
        self,
        name=None,
        comment=None,
        custom_host=None,
        custom_port=None,
        custom_protocol=None,
        custom_login=None,
        password=None,
    ):
        """
        only for external gates

        Parameters
        ----------

        custom_host: string
            The ftp host name

        custom_port: integer
            The port number

        custom_protocol: string
            "ftp", "sftp" or "ftps"

        custom_login: string
            The login of your ftp credetials

        password: string
            The password of your ftp credentials

        Returns
        -------

        """

        if self.get_base_feeder() is not None:
            print ("This gate is not external")
            return

        general_params = ["name", "comment"]
        params = {}
        for p in general_params:
            if locals()[p] is not None:
                params[p] = locals()[p]
        if len(params) > 0:
            self.update_general(**params)

        external_ftp_params = ["custom_host", "custom_port", "custom_protocol", "custom_login", "password"]
        params = {}
        for p in external_ftp_params:
            if locals()[p] is not None:
                params[p] = locals()[p]
        if len(params) > 0:
            client = get_client()
            client.partial_update(
                "odata/gate_ftp_accounts",
                self.ftp_account["id"],
                data=params
            )

        self.get_detailed_info()

        print(f"The gate {self.name} has been successfully updated")

    def list_dir(self, path="/"):

        """
        List files in the FTP directory

        Parameters
        ----------
        path: string
            Path to the directory you are interested in

        Returns
        -------
        List of files in the specified directory

        """

        return get_full_list(
            f"odata/gate_ftp_accounts/{self.ftp_account['id']}/list_dir/",
            params={"path": path}
        )

    def check_last_files(self, path="/", limit=20):
        dir_list = self.list_dir(path)
        files_list = [d["name"] for d in dir_list if d["type"]=="file"]
        files_list.sort(reverse=True)
        return files_list[:limit]

    @property
    def ftp_account_password(self):
        """

        Returns
        -------
        The password of the FTP

        """

        client = get_client()

        self._password = client.detail_route(
            "odata/gate_ftp_accounts",
            self.ftp_account['id'],
            "GET",
            "password"
        )["password"]

        return self._password


class BaseFeeder(ActivationMixin):

    def __init__(self, info):
        self._info = info
        self.__dict__.update(info)

        self.activable_object_model = "base_feeder"
        self.activable_object_id = self.id

    def get_detailed_info(self):
        """

        Returns
        -------

        A dictionary that contains all info about the Organization

        """

        client = get_client()

        info = client.retrieve(
            "odata/base_feeders",
            self.id
        )
        self._info = info
        self.__dict__.update(info)

        return self._info

    def create_generic_basic_feeder(self, script):

        client = get_client()

        generic_basic_feeder_info = client.create(
            "odata/generic_basic_feeders",
            data={
                "base_feeder": self.id,
                "script": script
            }
        )

        return GenericBasicFeeder(generic_basic_feeder_info)

    def get_generic_basic_feeder(self):
        """

        Returns
        -------

        """

        if self._info["child_model"] != "generic_basic_feeder":
            return GenericBasicFeeder({"id": self._info["child_id"]})
        else:
            print(f"BaseFeeder {self._info['name']} has no generic_basic_feeder")
            return

    def update(
        self,
        crontab=None,
        timezone=None
    ):
        """

        Parameters
        ----------
        crontab: string
        timezone

        Returns
        -------

        """

        args = ["crontab", "timezone"]
        params = {}
        for arg in args:
            if locals()[arg] is not None:
                params[arg] = locals()[arg]

        if len(params.keys()) == 0:
            print("No modifications to apply")
            return

        client = get_client()

        self.deactivate()
        client.partial_update(
            "odata/base_feeders",
            self.id,
            data=params
        )


class GenericBasicFeeder():

    def __init__(self, info):
        self._info = info
        self.__dict__.update(info)

    def get_detailed_info(self):
        """

        Returns
        -------

        A dictionary that contains all info about the Organization

        """

        client = get_client()

        info = client.retrieve(
            "odata/generic_basic_feeders",
            self.id
        )
        self._info = info
        self.__dict__.update(info)

        return self._info

    def update(self, script=None):
        """

        Parameters
        ----------
        script: string

        Returns
        -------

        """

        if (script is None):
            print("No modifications to apply")
            return

        client = get_client()
        client.partial_update(
            "odata/generic_basic_feeders",
            self.id,
            data={
                "script": script
            }
        )

