import ftputil
import unittest
import pandas as pd
from pprint import pprint

import openergy as op
import openergy.dev.project_configuration as opdev


class ConfigurationTest(unittest.TestCase):
    def setUp(self):

        prod_url = "https://data.openergy.fr"
        login = "user.test@openergy.fr"
        pwd = "usertest"

        self.client = op.set_client(login, pwd, prod_url)

        # Get organization
        self.organization = opdev.Organization.retrieve("Test Organization")

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

        self.assertTrue(self.project.get_gate("Test Internal Gate") is not None)

        r = opdev.Gate.retrieve("Test Organization", "Test Project", "Test Internal Gate")
        self.assertTrue(r is not None)

        # update internal gate infos
        self.internal_gate.update_internal(
            name="Internal Gate Test",
            crontab="1 1 1 * * *",
            script="Gate Script Test"
        )

        # create an external gate
        self.external_gate = self.project.create_external_gate(
            name="Test External Gate",
            custom_host=self.internal_gate.ftp_account["host"],
            custom_port=self.internal_gate.ftp_account["port"],
            custom_protocol=self.internal_gate.ftp_account["protocol"],
            custom_login=self.internal_gate.ftp_account["login"],
            password=self.internal_gate.ftp_account_password
        )

        self.assertTrue(self.project.get_gate("Test External Gate") is not None)

        r = opdev.Gate.retrieve("Test Organization", "Test Project", "Test External Gate")
        self.assertTrue(r is not None)

        # fill artificially a gate
        with ftputil.FTPHost(
                self.internal_gate.ftp_account["host"],
                self.internal_gate.ftp_account["login"],
                self.internal_gate.ftp_account_password) as ftp:
            with open("resources/config/test_data.csv", "rb") as source:
                with ftp.open("test_data.csv", "wb") as target:
                    target.write(source.read())

        # get parse_script
        with open("resources/config/parse_script.py", "r") as f:
            parse_script = f.read()

        # create an importer and activate it
        self.importer = self.project.create_importer(
            name="Test Importer",
            gate_name="Internal Gate Test",
            parse_script=parse_script,
            root_dir_path="/",
            crontab="0 0 0 * * *",
            waiting_for_outputs=True,
            outputs_length=2
        )

        self.assertTrue(self.project.get_importer("Test Importer") is not None)
        self.assertEqual(2, len(self.importer.get_outputs()))

        r = opdev.Importer.retrieve("Test Organization", "Test Project", "Test Importer")
        self.assertTrue(r is not None)
        print("r", r)

        # update importer infos
        self.importer.update(
            name="Importer Test",
            parse_script=parse_script + "\n",
            crontab="1 1 1 * * *"
        )

        # configure cleaner and activate it
        def unitcleaners_config_fct(se):

            return opdev.configure_unitcleaner(
                freq="10T",
                clock="gmt",
            )

        self.cleaner = self.project.get_cleaner(self.importer.name)

        self.cleaner.configure_all(
            unitcleaners_config_fct=unitcleaners_config_fct,
            activate=True,
            waiting_for_outputs=True,
            outputs_length=2
        )

        r = opdev.Cleaner.retrieve("Test Organization", "Test Project", "Importer Test")
        self.assertTrue(r is not None)

        # get analysis inputs_list
        self.inputs_list = self.cleaner.get_outputs()

        def inputs_config_fct(input_se):
            return opdev.get_analysis_input_config(
                input_series_name=input_se.name,
                column_name=f"{input_se.name} analyzed",
                input_series_generator=input_se.generator["id"]
            )

        # get outputs names list
        self.output_names_list = [f"{se.name} analyzed" for se in self.inputs_list]

        def outputs_config_fct(output_name):
            return opdev.get_analysis_output_config(
                name=output_name,
                unit=output_name.split(" ")[0],
                resample_rule="mean"
            )

        # create analysis and activate it

        # get parse_script
        with open("resources/config/analysis_script.py", "r") as f:
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

        self.assertTrue(self.project.get_analysis("Test Analysis") is not None)
        self.assertEqual(2, len(self.analysis.get_outputs()))

        r = opdev.Analysis.retrieve("Test Organization", "Test Project", "Test Analysis")
        self.assertTrue(r is not None)

        self.analysis.reset()
        self.assertEqual(2, len(self.analysis.get_outputs()))

        self.analysis.update(
            input_freq="3H",
            script=analysis_script + "\n"
        )

        # test data_scan
        df = self.project.data_scan()
        self.assertEqual(len(df), 6)

        # test check_last_files
        last_files = self.project.check_last_files()
        self.assertEqual(2, len(last_files.keys()))
        for gate, files in last_files.items():
            self.assertEqual('test_data.csv', files[0])

        # deletion tests
        self.cleaner.clear_all_configurations()
        self.assertEqual(len(self.cleaner.get_outputs()), 0)
