from .resources_general import resource_already_exists, activate_resource, waiting_for_outputs, deactivate_resource, delete_resource

def create_importer(
        client,
        project,
        importer_name,
        gate,
        parse_script,
        root_dir_path="/",
        crontab="",
        re_run_last_file=False,
        importer_comment="",
        activate=True,
        replace=False,
        wait_for_outputs=False,
        outputs_length=0
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: dictionary
        Project record

    importer_name: string
        The name of the importer

    gate: dictionary
        Gate record

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
        The nuùber of expected outputs.

    Returns
    -------

    The created importer record as a dictionary
    """


    if resource_already_exists(client, project, importer_name, "importer", replace):
        return

    print(f"Creation of importer {importer_name}")

    importer = client.create(
        "/odata/importers/",
        data={
            "project": project["odata"],
            "name": importer_name,
            "comment": importer_comment
        }
    )

    client.partial_update(
        "/odata/importers/",
        importer["id"],
        data={
            "gate": gate["id"],
            "root_dir_path": root_dir_path,
            "crontab": crontab,
            "parse_script": parse_script,
            "re_run_last_file": re_run_last_file
        }
    )

    print(f"The importer {importer_name} has been successfully created")

    if activate:
        activate_resource(client, importer, "importer")

        if wait_for_outputs:
            waiting_for_outputs(client, importer, "importer", outputs_length)

    return importer


def update_importer(
        client,
        importer,
        gate = None,
        parse_script=  None,
        root_dir_path= None,
        crontab= "",
        re_run_last_file= None,
        importer_name = None,
        importer_comment= None,
        activate=True,
        wait_for_outputs=False,
        outputs_length=0
):

    if importer["active"]:
        deactivate_resource(
            client,
            importer,
            "importer"
        )

    config_params={}

    if gate is not None:
        config_params["gate"] = gate["id"]
    if parse_script is not None:
        config_params["parse_script"] = parse_script
    if root_dir_path is not None:
        config_params["root_dir_path"] = root_dir_path
    if crontab is not None:
        config_params["crontab"] = crontab
    if re_run_last_file is not None:
        config_params["re_run_last_file"] = re_run_last_file

    if importer_name is not None:
        config_params["name"] = importer_name
    if importer_comment is not None:
        config_params["comment"] = importer_comment

    if len(config_params.keys()) == 0:
        return importer
    else:

        updated_importer = client.partial_update(
            "odata/importers",
            importer["id"],
            data= config_params
        )

        if activate:
            activate_resource(client, updated_importer, "importer")

            if wait_for_outputs:
                waiting_for_outputs(client, updated_importer, "importer", outputs_length)

        return updated_importer