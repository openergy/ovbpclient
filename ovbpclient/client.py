from .rest_client import RestClient

from .endpoints import BaseEndpoint
from .models import oteams as oteams_models, odata  as odata_models


class Client:
    def __init__(
            self,
            host,
            login,
            password,
            port=443,
            verify_ssl=True
    ):
        # todo: manage credentials properly
        self.rest_client = RestClient(
            host,
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
    def get_organization_by_name(self, name) -> "oteams_models.Organization":
        # todo: check name
        orgs_qs = self.organizations.list(limit=2, filter_by=dict(name=name))
        return orgs_qs.one()
