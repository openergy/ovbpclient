from openergy import set_client, CleanerConfigurator
from pprint import pprint

def get_client(src_account, dst_account):
    if dst_account is not None:
        return set_client(*dst_account)
    else:
        return set_client(*src_account)

def gate_copy(src_account, resource, new_resource, dst_account=None):

    gate = resource
    new_gate = new_resource

    # FTP ACCOUNT
    ftp_account = gate["ftp_account"]

    new_ftp_account_id = new_gate["ftp_account"]  # created automatically with the gate

    def retrieve_ftp_password(ftp_account):
        client = set_client(*src_account)
        r = client.detail_route("odata/gate_ftp_accounts", ftp_account["id"], "GET", "password")
        return r["password"]

    d_ftp = dict([
        ("custom_host", ftp_account["host"]),
        ("custom_port", ftp_account["port"]),
        ("custom_login", ftp_account["login"]),
        ("custom_protocol", ftp_account["protocol"]),
        ("password", retrieve_ftp_password(ftp_account))
    ])

    client = get_client(src_account, dst_account)
    new_ftp_account = client.partial_update("odata/gate_ftp_accounts", new_ftp_account_id, d_ftp)

    # FEEDER

    if gate["base_feeder"] is not None:
        base_feeder = gate["base_feeder"]

        client = set_client(*src_account)
        generic_basic_feeder = client.retrieve("odata/generic_basic_feeders", base_feeder["child_id"])

        d_base_feeder = dict([
            ("gate", new_gate["id"]),
            ("timezone", base_feeder["timezone"]),
            ("crontab", base_feeder["crontab"])
        ])

        client = get_client(src_account, dst_account)
        new_base_feeder = client.create("odata/base_feeders", d_base_feeder)

        d_generic_basic_feeder = dict([
            ("base_feeder", new_base_feeder["id"]),
            ("script", generic_basic_feeder["script"])
        ])

        client = get_client(src_account, dst_account)
        new_generic_basic_feeder = client.create("odata/generic_basic_feeders", d_generic_basic_feeder)

def importer_and_cleaner_copy(src_account, resource, new_resource, dst_odata_project_id=None, dst_account=None):

    # IMPORTER

    importer = resource
    new_importer = new_resource

    if dst_odata_project_id is not None:
        client = get_client(src_account, dst_account)
        gate_id = client.list("odata/gates", dict(project=dst_odata_project_id, name=importer["gate"]["name"]))["data"][0]["id"]
    else:
        gate_id = importer["gate"]["id"]

    d = dict([
        ("gate", gate_id),
        ("parse_script", importer["parse_script"]),
        ("crontab", importer["crontab"]),
        ("root_dir_path", importer["root_dir_path"]),
        ("re_run_last_file", importer["re_run_last_file"])
    ])

    client = get_client(src_account, dst_account)
    new_importer = client.partial_update("odata/importers", new_importer["id"], d)

    # CLEANER

    client = set_client(*src_account)
    cleaner = client.list("odata/cleaners", dict(project=importer["project"], name=importer["name"]))["data"][0]
    unitcleaners = list(client.list_iter_all("odata/unitcleaners", dict(cleaner=cleaner["id"])))

    if dst_odata_project_id is not None:
        client = get_client(src_account, dst_account)
        new_cleaner = client.list("odata/cleaners", dict(project=dst_odata_project_id, name=new_importer["name"]))["data"][0]
    else:
        client = set_client(*src_account)
        new_cleaner = client.list("odata/cleaners", dict(project=importer["project"], name=new_importer["name"]))["data"][0]

    for unitcleaner in unitcleaners:
        d_unitcleaner = dict([
            ("cleaner", new_cleaner["id"]),
            ("external_name", unitcleaner["external_name"]),
            # basic
            ("name", unitcleaner["name"]),
            ("freq", unitcleaner["freq"]),
            ("input_unit_type", unitcleaner["input_unit_type"]),
            ("input_convention", unitcleaner["input_convention"]),
            ("clock", unitcleaner["clock"]),
            ("timezone", unitcleaner["timezone"]),
            ("unit", unitcleaner["unit"]),
            ("label", unitcleaner["label"]),
            # advanced
            ("input_expected_regular", unitcleaner["input_expected_regular"]),
            ("unit_type", unitcleaner["unit_type"]),
            ("resample_rule", unitcleaner["resample_rule"]),
            ("interpolate_limit", unitcleaner["interpolate_limit"]),
            ("wait_offset", unitcleaner["wait_offset"]),
            ("operation_fct", unitcleaner["operation_fct"]),
            ("filter_fct", unitcleaner["filter_fct"]),
            ("derivative_filter_fct", unitcleaner["derivative_filter_fct"]),
            # expert
            ("custom_delay", unitcleaner["custom_delay"]),
            ("custom_fct", unitcleaner["custom_fct"]),
            ("custom_before_offset", unitcleaner["custom_before_offset"]),
            ("custom_after_offset", unitcleaner["custom_after_offset"]),
            ("numerical_filter", unitcleaner["numerical_filter"])
        ])
        new_unit_cleaner = client.create("odata/unitcleaners", d_unitcleaner)

def analysis_copy(src_account, resource, new_resource, dst_odata_project_id, dst_account=None):

    analysis = resource
    new_analysis = new_resource

    # INPUTS

    client = set_client(*src_account)
    inputs = list(client.list_iter_all("odata/analysis_inputs", dict(analysis=analysis["id"])))

    client = get_client(src_account, dst_account)
    for input in inputs:

        if dst_odata_project_id is None:
            input_series_generator_id = input["input_series_generator"]["id"]
        else:
            model = input["input_series_generator"]["model"]
            if model == "cleaner":
                generator_url = "odata/cleaners"
            elif model == 'analysis':
                generator_url = "odata/analyses"
            input_series_generator_id = client.list(generator_url, dict(name=input["input_series_generator"]["name"]))["data"][0]["id"]

        d_input = dict([
            ("analysis", new_analysis["id"]),
            ("column_name", input["column_name"]),
            ("input_series_name", input["input_series_name"]),
            ("input_series_generator", input_series_generator_id)
        ])
        new_input = client.create("odata/analysis_inputs", d_input)

    # CONFIG

    config = analysis["analysisconfig"]

    d_config = dict([
        ("analysis", new_analysis["id"]),

        # basic
        ("script_method", config["script_method"]),
        ("input_freq", config["input_freq"]),
        ("output_freq", config["output_freq"]),
        ("clock", config["clock"]),
        ("output_timezone", config["output_timezone"]),
        ("script", config["script"]),

        # expert
        ("start_with_first", config["start_with_first"]),
        ("wait_for_last", config["wait_for_last"]),
        ("before_offset_strict_mode", config["before_offset_strict_mode"]),
        ("custom_before_offset", config["custom_before_offset"]),
        ("custom_after_offset", config["custom_after_offset"]),

        # outputs
        ("custom_delay", config["custom_delay"]),
        ("wait_offset", config["wait_offset"])
    ])

    client = get_client(src_account, dst_account)
    new_config = client.create("odata/analysis_configs", d_config)

    # OUTPUTS

    client = set_client(*src_account)
    outputs = list(client.list_iter_all("odata/analysis_outputs", dict(analysis=analysis["id"])))

    client = get_client(src_account, dst_account)
    for output in outputs:
        d_output = dict([
            ("analysis", new_analysis["id"]),
            ("name", output["name"]),
            ("label", output["label"]),
            ("unit", output["unit"]),
            ("resample_rule", output["resample_rule"])
        ])
        new_output = client.create("odata/analysis_outputs", d_output)

def dashboard_copy(src_account, resource, new_resource, dst_odata_project_id, dst_account=None):

    dashboard = resource
    new_dashboard = new_resource

    # INPUTS

    client = set_client(*src_account)
    inputs = list(client.list_iter_all("odata/dashboard_inputs", dict(dashboard=dashboard["id"])))

    client = get_client(src_account, dst_account)
    for input in inputs:

        if dst_odata_project_id is None:
            input_series_generator_id = input["input_series_generator"]["id"]
        else:
            model = input["input_series_generator"]["model"]
            if model == "importer":
                generator_url = "odata/importers"
            elif model == "cleaner":
                generator_url = "odata/cleaners"
            elif model == 'analysis':
                generator_url = "odata/analyses"
            input_series_generator_id = client.list(generator_url, dict(name=input["input_series_generator"]["name"]))["data"][0]["id"]

        d_input = dict([
            ("dashboard", new_dashboard["id"]),
            ("column_name", input["column_name"]),
            ("input_series_name", input["input_series_name"]),
            ("input_series_generator", input_series_generator_id)
        ])
        new_input = client.create("odata/dashboard_inputs", d_input)

    # CONFIG

    d_dashboard = dict([
        ("dropna", dashboard["dropna"]),
        ("controller_script", dashboard["controller_script"]),
        ("content_script", dashboard["content_script"]),
        ("init_period", dashboard["init_period"]),
        ("frequency_mode", dashboard["frequency_mode"] if dashboard["frequency_mode"] is not None else ''),
        ("debug", dashboard["debug"])
    ])

    client = get_client(src_account, dst_account)
    new_dashbaord = client.partial_update("odata/dashboards", new_dashboard["id"], d_dashboard)


def copy_resource(src_account, resource_url, resource_id, dst_odata_project_id=None, dst_account=None, dst_resource_name=None):

    """
    :param src_account: (login, email, backend url)
    :param resource_url: "odata/gates", "odata/importers", "odata/analyses", "odata/dashboards"
    :param resource_id: resource uuid
    :param dst_odata_project_id (optional): odata project uuid ; only if the destination project is different from the source project.
    :param dst_account (optional):  (login, email, backend url) ; only if the account project is different from the source account.
    The destination account must have Write rights within the project.
    :param dst_resource_name (optional): to give the name of your choice to the copied resource, by default "(copy)" is added to the original name.
    :return:
    """

    client = set_client(*src_account)
    resource = client.retrieve(resource_url, resource_id)

    if dst_odata_project_id is None:
        #Same project
        new_odata_project_id = resource["project"]
    else:
        #New Project
        new_odata_project_id = dst_odata_project_id


    client = get_client(src_account, dst_account)
    if dst_resource_name is None:

        def find_new_name(initial_name, c):
            if c == 0:
                try_name = initial_name
            else:
                try_name = initial_name + " (copy %d)" % c
            resource_with_this_name = client.list(resource_url, dict(project=new_odata_project_id, name=try_name))["data"]
            if len(resource_with_this_name) == 1:
                return find_new_name(initial_name, c + 1)
            else:
                return try_name

        new_resource_name = find_new_name(resource["name"], 0)

    else:
        new_resource_name = dst_resource_name
        resource_with_this_name = client.list(resource_url, dict(project=new_odata_project_id, name=dst_resource_name))["data"]
        if len(resource_with_this_name) == 1:
            print("The resource %s %s already exists. Please find another name" % (resource_url, dst_resource_name))

    new_resource = client.create(resource_url, dict(name=new_resource_name, comment=resource["comment"],project=new_odata_project_id))

    print("New %s created with name %s" % (resource_url, new_resource["name"]))

    if resource_url == "odata/gates":
        gate_copy(src_account, resource, new_resource, dst_account)

    elif resource_url == "odata/importers":
        importer_and_cleaner_copy(src_account, resource, new_resource, dst_odata_project_id, dst_account)

    elif resource_url == "odata/analyses":
        analysis_copy(src_account, resource, new_resource, dst_odata_project_id, dst_account)

    elif resource_url == "odata/dashboards":
        dashboard_copy(src_account, resource, new_resource, dst_odata_project_id, dst_account)

def copy_data_project(src_account, project_id, dst_organization_id=None, dst_account=None, dst_project_name=None):

    """
    :param src_account: (login, email, backend url)
    :param project_id: project uuid
    :param dst_organization_id (optional): destination organization uuid ; only if the destination organization is different from the source organization.
    :param dst_account (optional):  (login, email, backend url) ; only if the account project is different from the source account.
    The destination account must have Create Rights within the destination organization to be able to create a new project.
    :param dst_project_name (optional): to give the name of your choice to the copied project, by default "(copy)" is added to the original name.
    :return:
    """

    project_url = "oteams/projects"
    gate_url = "odata/gates"
    importer_url = "odata/importers"
    analysis_url = "odata/analyses"
    dashboard_url = "odata/dashboards"

    client = set_client(*src_account)
    project = client.retrieve(project_url, project_id)

    if dst_organization_id is not None:
        new_organization_id = dst_organization_id
    else:
        new_organization_id = project["organization"]["id"]

    client = get_client(src_account, dst_account)
    if dst_project_name is None:

        def find_new_name(initial_name, c):
            if c == 0:
                try_name = initial_name
            else:
                try_name = initial_name + " (copy %d)" % c

            project_with_this_name = client.list(project_url, dict(organization=new_organization_id, name=try_name))["data"]

            if len(project_with_this_name) >= 1:
                return find_new_name(initial_name, c + 1)
            else:
                return try_name

        new_project_name = find_new_name(project["name"], 0)

    else:
        new_project_name = dst_project_name
        project_with_this_name = client.list(project_url, dict(organization=new_organization_id, name=dst_project_name))["data"]
        if len(project_with_this_name) == 1:
            print("The project %s already exists in the requested organization. Please find another name" % dst_project_name)


    new_project = client.create(project_url, dict(name=new_project_name, comment=project["comment"], organization=new_organization_id))

    print("New project created with name %s" % new_project_name)

    client = set_client(*src_account)
    for resource_url in [gate_url, importer_url, analysis_url, dashboard_url]:

        resource_list = list(client.list_iter_all(resource_url, dict(project=project["odata"])))

        for resource in resource_list:
            copy_resource(src_account, resource_url, resource["id"], new_project["odata"], dst_account)


if __name__ == "__main__":

    _src_account = ("solene.gerphagnon@openergy.fr", "h82KSJwCgF", "https://data.openergy.fr")
    _dst_account = ("solene.gerphagnon@openergy.fr", "h82KSJwCgF", "https://test1.openergy.fr")

    #copy_resource(_src_account, "odata/analyses", "bbcec889-121a-43cf-aa18-d27120648c78")
    #copy_resource(_src_account, "odata/importers", "e1a9d6f0-ba6d-492a-8624-5ed72519b83d")
    #copy_resource(_src_account, "odata/gates", "2a939c16-633d-4462-b03a-9514e2de56a4")
    #copy_data_project(src_account=_src_account, project_id="68152f98-edc9-4fbc-9869-405c60f41bcf", dst_organization_id="32606ad2-159c-4890-a1d7-eca2bdd1a3c7" ,dst_account=_dst_account)