 # ovbpclient

 ## initialization



 ### imports

	import os
	import datetime as dt
	import pprint

	import pandas as pd

	from ovbpclient import Client, RecordDoesNotExistError


 ### prepare client


	# auth file is a text file with two lines: the first one contains login, the second password
	client = Client(AUTH_PATH)


 ## Project



	organization = client.get_organization(ORGANIZATION_NAME)
	project_name = "Ovbpclient documentation"
	try:
	    project = organization.get_project(project_name)
	except RecordDoesNotExistError:
	    project = organization.create_project(project_name)

	print(project)
	print()
	pprint.pprint(project.data)


*out:*

	<oteams/projects: Ovbpclient documentation (89bcfaa0-3792-4218-837b-ee3089207360)>

	OrderedDict([('id', '89bcfaa0-3792-4218-837b-ee3089207360'),
	             ('rights', None),
	             ('odata', '0d9b1d54-8fe7-4925-9b16-3d3636c467af'),
	             ('obuildings', '38fbf2d7-de4f-44d3-b820-9760b2ccdb7c'),
	             ('is_visible', True),
	             ('organization',
	              OrderedDict([('id', '32606ad2-159c-4890-a1d7-eca2bdd1a3c7'),
	                           ('rights', None),
	                           ('name', 'Openergy'),
	                           ('comment', ''),
	                           ('control_affiliations', False),
	                           ('log_activity', False),
	                           ('ftp_account',
	                            '1b56e75e-0b40-4e03-9701-ef66bb42253b')])),
	             ('name', 'Ovbpclient documentation'),
	             ('comment', ''),
	             ('private_comment', ''),
	             ('creation_date', '2020-04-13'),
	             ('display_buildings', False)])


 Other syntax to directly access project:


	project = client.get_project(ORGANIZATION_NAME, project_name)


 ## Gate




 ### Create gate

	# create gate if it does not exist
	gate_name = "gate"
	try:
	    gate = project.get_gate(gate_name)
	except RecordDoesNotExistError:
	    # create gate
	    gate = project.create_gate(gate_name, comment="documentation gate")

	    # attach internal ftp account
	    gate.attach_internal_ftp_account()


 ### Upload file


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

 ## Importer

 ### Create and configure



 prepare name and script

	importer_name = "importer-a"
	importer_script = """
	import pandas as pd

	def parse(content_bytes, rel_path, **tools):
	    return pd.read_json(content_bytes)

	"""


 create importer if it does not exist

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


*out:*

	<odata/importers: importer-a (f7e0621b-f2d2-4bd7-9e8b-3e807ca3547c)>

	OrderedDict([('id', 'f7e0621b-f2d2-4bd7-9e8b-3e807ca3547c'),
	             ('rights', None),
	             ('active', False),
	             ('name', 'importer-a'),
	             ('comment', 'documentation importer'),
	             ('model', 'importer'),
	             ('crontab', '0 0 0 1 1 *'),
	             ('auto_partial_reset', False),
	             ('parse_script',
	              '\n'
	              'import pandas as pd\n'
	              '\n'
	              'def parse(content_bytes, rel_path, **tools):\n'
	              '    return pd.read_json(content_bytes)\n'
	              '\n'),
	             ('root_dir_path', '/'),
	             ('re_run_last_file', False),
	             ('notify_missing_files_nb', 0),
	             ('max_ante_scanned_files_nb', 0),
	             ('last_run', datetime.datetime(2020, 4, 13, 11, 46, 42, 41112)),
	             ('last_clear', datetime.datetime(2020, 4, 10, 16, 54, 40, 854481)),
	             ('last_imported_path', 'first.json'),
	             ('latest_imported_mdate', '2020-04-10T13:18:51Z'),
	             ('project', '0d9b1d54-8fe7-4925-9b16-3d3636c467af'),
	             ('gate', '0af8ead9-612a-46f8-a250-8545937101aa')])

 ### Run, activate, deactivate


	# run
	importer.run()

	# activate if off
	if not importer.active:
	    importer.activate()

	# deactivate
	importer.deactivate()


 ### Work with series



 wait for run to finish

	time.sleep(5)


 retrieve all series

	importer_series = importer.list_all_output_series()
	for se in importer_series:
	    print(se)


*out:*

	<odata/series: c (90a794f4-1439-4338-9a29-1c9d8e75d1d0)>
	<odata/series: a (7a6c8e06-abe0-4f23-b81e-45af2a27c028)>
	<odata/series: b (bb31ab30-a9f4-46ef-80d4-03c365962bd1)>

 get output dataframe

	importer_df = client.series.select_data(
	    importer_series,
	    start=dt.datetime(2012, 1, 1, 6),
	    end=dt.datetime(2012, 1, 1, 12)
	)
	print(importer_df)


*out:*

	                       b    a    c
	2012-01-01 06:00:00  2.0  1.0  3.0
	2012-01-01 07:00:00  2.0  1.0  3.0
	2012-01-01 08:00:00  2.0  1.0  3.0
	2012-01-01 09:00:00  2.0  1.0  3.0
	2012-01-01 10:00:00  2.0  1.0  3.0
	2012-01-01 11:00:00  2.0  1.0  3.0
	2012-01-01 12:00:00  2.0  1.0  3.0

 get output series

	series_0 = importer_series[0]
	series_0_se = series_0.select_data(end=dt.datetime(2012, 1, 1, 4))
	print(series_0_se)


*out:*

	2012-01-01 00:00:00    3.0
	2012-01-01 01:00:00    3.0
	2012-01-01 02:00:00    3.0
	2012-01-01 03:00:00    3.0
	2012-01-01 04:00:00    3.0
	dtype: float64

 ## Cleaner



 ### Configure
 retrieve cleaner

	cleaner = project.get_cleaner(importer_name)
	print(cleaner)
	print()
	pprint.pprint(cleaner.data)


*out:*

	<odata/cleaners: importer-a (c49b62ff-3f9d-4db4-9d93-b47c8eb77c00)>

	OrderedDict([('id', 'c49b62ff-3f9d-4db4-9d93-b47c8eb77c00'),
	             ('rights', None),
	             ('name', 'importer-a'),
	             ('comment', ''),
	             ('model', 'cleaner'),
	             ('last_run', datetime.datetime(2020, 4, 13, 13, 28, 28, 462518)),
	             ('last_clear', datetime.datetime(2020, 4, 10, 7, 57, 15, 399946)),
	             ('project', '0d9b1d54-8fe7-4925-9b16-3d3636c467af'),
	             ('related_importer', 'f7e0621b-f2d2-4bd7-9e8b-3e807ca3547c')])

 delete unitcleaners if any

	for uc in cleaner.list_all_unitcleaners():
	    uc.delete()


 configure unitcleaners

	for se in cleaner.list_all_importer_series():
	    cleaner.create_unitcleaner(
	        se.name,
	        name=f"{se.name}-cleaned",
	        freq="1H"
	    )
	unitcleaners = cleaner.list_all_unitcleaners()
	for uc in unitcleaners:
	    print(uc)


*out:*

	<odata/unitcleaners: b-cleaned (05d153c4-e452-4971-b0fd-1ed5176ef5d5)>
	<odata/unitcleaners: a-cleaned (a4dc6e12-2d9e-45c9-b6ea-cef97276e3ad)>
	<odata/unitcleaners: c-cleaned (01ce29fd-5ce6-496e-802b-dd67ebaf44f3)>

 ### Configure using excel
 export configuration to excel

	xlsx_path = os.path.join(WORK_DIR_PATH, f"{importer_name}.xlsx")
	cleaner.export_configuration_to_excel(xlsx_path)


 after modifying configuration, upload new configuration

	cleaner.configure_from_excel(xlsx_path)


 ### Work with series



 wait for run to finish

	time.sleep(5)


 retrieve series and data

	cleaner_series = cleaner.list_all_output_series()
	for se in cleaner_series:
	    print(se)
	cleaner_df = client.series.select_data(
	    cleaner_series,
	    end=dt.datetime(2012, 1, 1, 4)
	)
	print(cleaner_df)


*out:*

	<odata/series: b-cleaned (a12ccd9b-9354-41dc-bcdf-92b455233248)>
	<odata/series: a-cleaned (e14da853-f384-4b36-8e21-b369f322dd76)>
	<odata/series: c-cleaned (f9f8775b-3a58-400d-93d5-ace322192f1f)>
	                     c-cleaned  a-cleaned  b-cleaned
	2012-01-01 01:00:00        3.0        1.0        2.0
	2012-01-01 02:00:00        3.0        1.0        2.0
	2012-01-01 03:00:00        3.0        1.0        2.0
	2012-01-01 04:00:00        3.0        1.0        2.0

 ## Analysis



 ### create and configure



 create analysis if it does not exist

	analysis_name = "analysis-a"
	try:
	    analysis = project.get_analysis(analysis_name)
	except RecordDoesNotExistError:
	    analysis = project.create_analysis(analysis_name, comment="documentation analysis")

	print(analysis)
	print()
	pprint.pprint(analysis.data)


*out:*

	<odata/analyses: analysis-a (aa2940e9-cc7e-47ea-87c8-6a7bffb866f3)>

	OrderedDict([('id', 'aa2940e9-cc7e-47ea-87c8-6a7bffb866f3'),
	             ('rights', None),
	             ('analysisconfig', 'b05eaa68-795c-453f-a02b-8bc6b1228ba1'),
	             ('active', True),
	             ('name', 'analysis-a'),
	             ('comment', 'documentation analysis'),
	             ('model', 'analysis'),
	             ('last_run', datetime.datetime(2020, 4, 13, 13, 28, 39, 804879)),
	             ('last_clear', None),
	             ('project', '0d9b1d54-8fe7-4925-9b16-3d3636c467af')])

 configure inputs if not already done

	analysis_inputs = analysis.list_all_analysis_inputs()
	if len(analysis_inputs) == 0:
	    # inputs: based on a-cleaned and b-cleaned series
	    input_names = [uc.name for uc in unitcleaners if uc.name[0] in ("a", "b")]
	    for name in input_names:
	        analysis.create_analysis_input(cleaner, name, name)
	    analysis_inputs = analysis.list_all_analysis_inputs()
	for ai in analysis_inputs:
	    print(ai)


*out:*

	<odata/analysis_inputs: caf321b7-3013-4699-861b-883da6a6b5cb>
	<odata/analysis_inputs: ba8230dd-843c-4320-8c3e-aa0ce1d1b941>

 configure outputs if not already done

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


*out:*

	<odata/analysis_outputs: a-output (7deda1bb-584c-4bde-809c-2183e286aa94)>

 prepare analysis script

	analysis_script = """
	import pandas as pd

	def analyze(df, **tools):
	    return pd.DataFrame({"a-output": df.mean(axis=1)})

	"""


 configure analysis config if not already done

	if analysis.get_analysis_config() is None:
	    analysis.create_analysis_config(
	        "3H",
	        "3H",
	        analysis_script
	    )


 reload analysis data and check configured

	analysis.reload()
	pprint.pprint(analysis.data)


*out:*

	OrderedDict([('id', 'aa2940e9-cc7e-47ea-87c8-6a7bffb866f3'),
	             ('rights',
	              OrderedDict([('can_delete', True),
	                           ('can_read', True),
	                           ('can_admin', True),
	                           ('can_write', True)])),
	             ('analysisconfig',
	              OrderedDict([('id', 'b05eaa68-795c-453f-a02b-8bc6b1228ba1'),
	                           ('rights', None),
	                           ('output_tags', []),
	                           ('clock', 'tzt'),
	                           ('output_timezone', 'Europe/Paris'),
	                           ('start_with_first', False),
	                           ('wait_for_last', False),
	                           ('input_freq', '3H'),
	                           ('output_freq', '3H'),
	                           ('custom_before_offset', None),
	                           ('custom_after_offset', None),
	                           ('before_offset_strict_mode', False),
	                           ('with_tags', False),
	                           ('script',
	                            '\n'
	                            'import pandas as pd\n'
	                            '\n'
	                            'def analyze(df, **tools):\n'
	                            '    return pd.DataFrame({"a-output": '
	                            'df.mean(axis=1)})\n'
	                            '\n'),
	                           ('script_method', 'array'),
	                           ('wait_offset', '6H'),
	                           ('custom_delay', None),
	                           ('analysis',
	                            'aa2940e9-cc7e-47ea-87c8-6a7bffb866f3')])),
	             ('active', True),
	             ('is_obsolete', False),
	             ('unresolved_notifications_nb', 0),
	             ('name', 'analysis-a'),
	             ('comment', 'documentation analysis'),
	             ('model', 'analysis'),
	             ('last_run', datetime.datetime(2020, 4, 13, 13, 28, 39, 804879)),
	             ('last_clear', None),
	             ('project', '0d9b1d54-8fe7-4925-9b16-3d3636c467af')])

 run analysis

	analysis.run()


 activate if analysis is off

	if not analysis.active:
	    analysis.activate()


 ### Work with series



 wait for run to finish

	time.sleep(5)


 retrieve series and data

	analysis_series = analysis.list_all_output_series()
	analysis_df = client.series.select_data(analysis_series)
	print(analysis_df)


*out:*

	                     a-output
	2012-01-01 03:00:00       1.5
	2012-01-01 06:00:00       1.5
	2012-01-01 09:00:00       1.5
	2012-01-01 12:00:00       1.5
	2012-01-01 15:00:00       1.5
	2012-01-01 18:00:00       1.5

 ## Project overview



 list and display records by type

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


*out:*

	Gates:
		<odata/gates: gate (0af8ead9-612a-46f8-a250-8545937101aa)>

	Importers:
		<odata/importers: importer-a (f7e0621b-f2d2-4bd7-9e8b-3e807ca3547c)>

	Cleaners:
		<odata/cleaners: importer-a (c49b62ff-3f9d-4db4-9d93-b47c8eb77c00)>

	Analyses:
		<odata/analyses: analysis-a (aa2940e9-cc7e-47ea-87c8-6a7bffb866f3)>

	Non-resolved notifications:


