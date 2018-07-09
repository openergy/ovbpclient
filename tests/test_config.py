import ftputil
import unittest
from pprint import pprint

import openergy as op
from openergy.dev.project_configuration import *


class ConfigurationTest(unittest.TestCase):
    def setUp(self):

        prod_url = "https://data.openergy.fr"
        login = "user.test@openergy.fr"
        pwd = "usertest"

        self.client = op.set_client(login, pwd, prod_url)

        # Get organization
        self.organization = Organization.retrieve("Test Organization")

        # Get the number of projects
        self.projects = self.organization.get_all_projects()

        # If > 0, delete all projects
        for p in self.projects:
            p.delete()

        self.projects = self.organization.get_all_projects()
        self.assertEqual(0, len(self.projects))

    def test_config(self):

        # create a project
        self.project = self.organization.create_project(
            "Test Project",
            "Test Comment",
            replace=True
        )

        self.assertTrue(self.organization.get_project("Test Project") is not None)

        # create an internal gate and activate it
        self.internal_gate = self.project.create_internal_gate(
            name="Test Internal Gate",
            timezone="Europe/Paris",
            crontab="0 0 0 * * *",
            script="Test Gate Script",
            activate=True
        )

        self.assertTrue(self.project.get_resource("gate", "Test Internal Gate") is not None)

        self.internal_gate.get_detailed_info()

        pprint(self.internal_gate._info)

        # create an external gate
        self.external_gate = self.project.create_external_gate(
            name="Test External Gate",
            host=self.internal_gate.ftp_account["host"],
            port=self.internal_gate.ftp_account["port"],
            protocol=self.internal_gate.ftp_account["protocol"],
            login=self.internal_gate.ftp_account["login"],
            password=self.internal_gate.ftp_account_password
        )

        self.assertTrue(self.project.get_resource("gate", "Test External Gate") is not None)

        # fill artificially a gate
        with ftputil.FTPHost(self.internal_gate.host, self.internal_gate.login, self.internal_gate.password) as ftp:
            with open("resources/Test File.csv", "rb") as source:
                with ftp.open("Test File.csv", "wb") as target:
                    target.write(source.content())

        # get parse_script
        with open("resources/parse_script", "r") as f:
            parse_script = f.read()

        # create an importer and activate it
        importer = self.project.create_importer(
            name="Test Importer",
            gate_name="Test Internal Gate",
            parse_script=parse_script,
            root_dir_path="/",
            crontab="0 0 0 * * *",
            waiting_for_outputs=True,
            outputs_length=2
        )

        self.assertTrue(self.project.get_resource("importer", "Test Importer") is not None)
        self.assertEqual(2, len(self.importer.get_outputs()))

        # configure cleaner and activate it
        def unit_cleaner_config_fct(se):

            return get_unitcleaner_config(
                external_name=se["external_name"],
                name=se["external_name"],
                freq="10T",
                input_unit_type="instantaneous",
                unit_type="instantaneous",
                input_convention="left",
                clock="gmt",
                timezone="Europe/Paris",
                unit=se["external_name"],
                resample_rule="mean"
            )

        self.cleaner = self.project.get_resource("cleaner", importer.name)
        self.cleaner.configure_all(
            unitcleaner_config_fct=unit_cleaner_config_fct,
            activate=True,
            waiting_for_outputs=True,
            outputs_length=2
        )

        self.assertTrue(self.project.get_resource("cleaner", "Test Importer") is not None)
        self.assertEqual(2, len(self.cleaner.get_outputs()))

        # get analysis inputs_list
        self.inputs_list = self.cleaner.get_outputs()

        def inputs_config_fct(input_se):
            return get_analysis_input_config(
                input_series_name=input_se.name,
                column_name=input_se.name,
                input_series_generator=input_se.generator["id"]
            )

        # get outputs names list
        self.output_names_list = [f"{se.name} analyzed" for se in self.inputs_list]

        def outputs_config_fct(output_name):
            return get_analysis_output_config(
                name=output_name,
                unit=output_name.split(" ")[0],
                resample_rule="mean"
            )

        # create analysis and activate it

        # get parse_script
        with open("resources/analysis_script", "r") as f:
            analysis_script = f.read()

        self.analysis = self.project.create_analysis(
            name="Test Analysis",
            inputs_list=self.inputs_list,
            inputs_config_fct=inputs_config_fct,
            output_names_list=self.output_names_list,
            outputs_config_fct=outputs_config_fct,
            input_freq="1H",
            output_freq="6H",
            clock="gmt",
            output_timezone="Europe/Paris",
            script=analysis_script,
            activate=True,
            waiting_for_outputs=True,
            outputs_length=2
        )

        self.assertTrue(self.project.get_resource("analysis", "Test Analysis") is not None)
        self.assertEqual(2, len(self.analysis.get_outputs()))
