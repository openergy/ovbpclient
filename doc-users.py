import json
import time


with open("gitignore/doc-users-info.json") as f:
    data = json.load(f)

ORGANIZATION_NAME = data["organization_name"]
AUTH_PATH = "gitignore/pass.txt"
WORK_DIR_PATH = "gitignore"

#@ # ovbpclient
#@
#@ ## initialization

#@ ### imports
import os
import datetime as dt
import pprint

import pandas as pd

from ovbpclient import Client, RecordDoesNotExistError

#@ ### prepare client

# auth file is a text file with two lines: the first one contains login, the second password
client = Client(AUTH_PATH)

## ---------------------------------------------------------------------------------------------------------------------
## ----------------------------------------------- project -------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
#@ ## Project
#@

organization = client.get_organization(ORGANIZATION_NAME)
project_name = "Ovbpclient documentation"
try:
    project = organization.get_project(project_name)
except RecordDoesNotExistError:
    project = organization.create_project(project_name)

print(project)
print()
pprint.pprint(project.data)

#@
#@ Other syntax to directly access project:

project = client.get_project(ORGANIZATION_NAME, project_name)

## ---------------------------------------------------------------------------------------------------------------------
## ------------------------------------------------- gate --------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
#@ ## Gate
#@

#@ ### Create gate
# create gate if it does not exist
gate_name = "gate"
try:
    gate = project.get_gate(gate_name)
except RecordDoesNotExistError:
    # create gate
    gate = project.create_gate(gate_name, comment="documentation gate")

    # attach internal ftp account
    gate.attach_internal_ftp_account()

#@ ### Upload file

# prepare file content
df = pd.DataFrame(
    dict(a=[1]*24, b=[2]*24, c=[3]*24),
    index=pd.date_range("01/01/2012", periods=24, freq="H")
)
content = df.to_json()

# upload
with gate.get_ftputil_client() as ftp_client:
    # for more info on ftputil_client: https://ftputil.sschwarzer.net/trac/wiki/Documentation
    with ftp_client.open("first.json", "w") as f:
        f.write(content)
## ---------------------------------------------------------------------------------------------------------------------
## ----------------------------------------------- importer ------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
#@ ## Importer
#@
#@ ### Create and configure

#@ prepare name and script
importer_name = "importer-a"
importer_script = """
import pandas as pd

def parse(content_bytes, rel_path, **tools):
    return pd.read_json(content_bytes)

"""

#@ create importer if it does not exist
try:
    importer = project.get_importer(importer_name)
except RecordDoesNotExistError:
    # create importer
    importer = project.create_importer(importer_name, comment="documentation importer")

    # configure
    importer.configure(
        gate,
        parse_script=importer_script,
        crontab="0 0 0 1 1 *"  # every 01/01 00:00 for each year
    )

print(importer)
print()
pprint.pprint(importer.data)

#@ ### Run, activate, deactivate

# run
importer.run()

# activate if off
if not importer.active:
    importer.activate()

# deactivate
importer.deactivate()

#@ ### Work with series

#@ wait for run to finish
time.sleep(5)

#@ retrieve all series
importer_series = importer.list_all_output_series()
for se in importer_series:
    print(se)

#@ get output dataframe
importer_df = client.series.select_data(
    importer_series,
    start=dt.datetime(2012, 1, 1, 6),
    end=dt.datetime(2012, 1, 1, 12)
)
print(importer_df)

#@ get output series
series_0 = importer_series[0]
series_0_se = series_0.select_data(end=dt.datetime(2012, 1, 1, 4))
print(series_0_se)

## ---------------------------------------------------------------------------------------------------------------------
## ----------------------------------------------- cleaner -------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
#@ ## Cleaner

#@ ### Configure
#@ retrieve cleaner
cleaner = project.get_cleaner(importer_name)
print(cleaner)
print()
pprint.pprint(cleaner.data)

#@ delete unitcleaners if any
for uc in cleaner.list_all_unitcleaners():
    uc.delete()

#@ configure unitcleaners
for se in cleaner.list_all_importer_series():
    cleaner.create_unitcleaner(
        se.name,
        name=f"{se.name}-cleaned",
        freq="1H"
    )
unitcleaners = cleaner.list_all_unitcleaners()
for uc in unitcleaners:
    print(uc)

#@ ### Configure using excel
#@ export configuration to excel
xlsx_path = os.path.join(WORK_DIR_PATH, f"{importer_name}.xlsx")
cleaner.export_configuration_to_excel(xlsx_path)

#@ after modifying configuration, upload new configuration
cleaner.configure_from_excel(xlsx_path)

#@ ### Work with series

#@ wait for run to finish
time.sleep(5)

#@ retrieve series and data
cleaner_series = cleaner.list_all_output_series()
for se in cleaner_series:
    print(se)
cleaner_df = client.series.select_data(
    cleaner_series,
    end=dt.datetime(2012, 1, 1, 4)
)
print(cleaner_df)

## ---------------------------------------------------------------------------------------------------------------------
## ----------------------------------------------- analysis ------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
#@ ## Analysis

#@ ### create and configure

#@ create analysis if it does not exist
analysis_name = "analysis-a"
try:
    analysis = project.get_analysis(analysis_name)
except RecordDoesNotExistError:
    analysis = project.create_analysis(analysis_name, comment="documentation analysis")

print(analysis)
print()
pprint.pprint(analysis.data)

#@ configure inputs if not already done
analysis_inputs = analysis.list_all_analysis_inputs()
if len(analysis_inputs) == 0:
    # inputs: based on a-cleaned and b-cleaned series
    input_names = [uc.name for uc in unitcleaners if uc.name[0] in ("a", "b")]
    for name in input_names:
        analysis.create_analysis_input(cleaner, name, name)
    analysis_inputs = analysis.list_all_analysis_inputs()
for ai in analysis_inputs:
    print(ai)

#@ configure outputs if not already done
analysis_outputs = analysis.list_all_analysis_outputs()
if len(analysis_outputs) == 0:
    analysis.create_analysis_output(
        "a-output",
        "mean",
        unit="°C"
    )
    analysis_outputs = analysis.list_all_analysis_outputs()
for ao in analysis_outputs:
    print(ao)

#@ prepare analysis script
analysis_script = """
import pandas as pd

def analyze(df, **tools):
    return pd.DataFrame({"a-output": df.mean(axis=1)})

"""

#@ configure analysis config if not already done
if analysis.get_analysis_config() is None:
    analysis.create_analysis_config(
        "3H",
        "3H",
        analysis_script
    )

#@ reload analysis data and check configured
analysis.reload()
pprint.pprint(analysis.data)

#@ run analysis
analysis.run()

#@ activate if analysis is off
if not analysis.active:
    analysis.activate()

#@ ### Work with series

#@ wait for run to finish
time.sleep(5)

#@ retrieve series and data
analysis_series = analysis.list_all_output_series()
analysis_df = client.series.select_data(analysis_series)
print(analysis_df)

## ---------------------------------------------------------------------------------------------------------------------
## ------------------------------------------ project overview ---------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
#@ ## Project overview

#@ list and display records by type
print("Gates:")
for gate in project.list_all_gates():
    print(f"\t{gate}")

print("\nImporters:")
for importer in project.list_all_importers():
    print(f"\t{importer}")

print("\nCleaners:")
for cleaner in project.list_all_cleaners():
    print(f"\t{cleaner}")

print("\nAnalyses:")
for analysis in project.list_all_analyses():
    print(f"\t{analysis}")

print(f"\nNon-resolved notifications:")
for notification in project.list_all_notifications(resolved=False):
    print(f"\t{notification}")

## ---------------------------------------------------------------------------------------------------------------------
## ----------------------------------------------- cleanup -------------------------------------------------------------
## ---------------------------------------------------------------------------------------------------------------------
#@
pass
