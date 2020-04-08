import getpass
import re
from .rest_client import RestClient
from .endpoints import BaseEndpoint
from .models import oteams as oteams_models, odata  as odata_models
from .util import get_one_and_only_one


class Client:
    def __init__(
            self,
            url="https://data.openergy.fr/api/v2",
            auth_buffer_or_path=None,
            verify_ssl=True
    ):
        # retrieve login/password
        if auth_buffer_or_path is None:
            login = input("Login: ")
            password = getpass.getpass()
        else:
            # prepare credentials str
            if isinstance(auth_buffer_or_path, str):
                with open(auth_buffer_or_path) as f:
                    auth_str = f.read()
            else:
                auth_str = auth_buffer_or_path.read()

            # parse
            auth_l = auth_str.strip().split("\n")
            if len(auth_l) < 2:
                raise ValueError("could not parse auth should be:\nlogin\npassword")
            login, password = auth_l[:2]

        # initialize rest client
        self.rest_client = RestClient(
            url,
            login,
            password,
            verify_ssl=verify_ssl
        )

        # oteams
        self.organizations = BaseEndpoint(
            self,
            "oteams/organizations",
            model_cls=oteams_models.Organization)
        self.projects = BaseEndpoint(
            self,
            "oteams/projects",
            model_cls=oteams_models.Project
        )

        # odata - projects
        self.odata_projects = BaseEndpoint(
            self,
            "odata/projects"
        )

        # odata - gates
        self.gates = BaseEndpoint(
            self,
            "odata/gates",
            model_cls=odata_models.Gate
        )
        self.base_feeders = BaseEndpoint(
            self,
            "odata/base_feeders",
            model_cls=odata_models.BaseFeeder
        )
        self.gate_ftp_accounts = BaseEndpoint(
            self,
            "odata/gate_ftp_accounts",
            model_cls=odata_models.GateFtpAccount
        )

        # odata - importers
        self.importers = BaseEndpoint(
            self,
            "odata/importers",
            model_cls=odata_models.Importer
        )
        self.importer_series = BaseEndpoint(
            self,
            "odata/importer_series"
        )

        # odata - cleaners
        self.cleaners = BaseEndpoint(
            self,
            "odata/cleaners",
            model_cls=odata_models.Cleaner
        )
        self.unitcleaners = BaseEndpoint(
            self,
            "odata/unitcleaners"
        )

        # odata - analysis
        self.analyses = BaseEndpoint(
            self,
            "odata/analyses",
            model_cls=odata_models.Analysis
        )
        self.analysis_configs = BaseEndpoint(
            self,
            "odata/analysis_configs"
        )
        self.analysis_inputs = BaseEndpoint(
            self,
            "odata/analysis_inputs"
        )
        self.analysis_outputs = BaseEndpoint(
            self,
            "odata/analysis_outputs"
        )

        # odata - notifications
        self.notifications = BaseEndpoint(
            self,
            "odata/notifications"
        )

    # --- organization
    def get_organization(self, name) -> "oteams_models.Organization":
        orgs = self.organizations.list(limit=2, filter_by=dict(name=name))
        return get_one_and_only_one(orgs)

    # -- project
    def get_project(self, organization_name, project_name) -> "oteams_models.Project":
        org = self.get_organization(organization_name)
        return org.get_project(project_name)
