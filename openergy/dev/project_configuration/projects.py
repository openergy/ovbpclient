def get_project(
        client,
        project_id
):
    return client.retrieve(
        "oteams/projects",
        project_id
    )


def get_project_from_name(
        client,
        organization,
        project_name
):
    """
    Get a single project record, knowing only its name and organization

    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    organization: dictionary
        Organization record

    project_name: string
        The name of the project

    Returns
    -------

    The project record as a dictionary

    """

    project = client.list(
        "/oteams/projects/",
        params={
            "organization": organization["id"],
            "name": project_name
        }
    )["data"]

    if len(project) == 0:
        print(f"No project named {project_name} in this organization")
        return
    elif len(project) == 1:
        return project[0]
    else:
        print(f"Several results found... Houston, we got a problem!")
        return


def create_project(
        client,
        organization,
        project_name,
        display_buildings=True,
        project_comment=""
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    organization: dictionary
        Organization record

    project_name: string
        The name of the project

    display_buildings: boolean
        Decides if the building section is displayed on the platform for this project

    project_comment: string
        An optional comment

    Returns
    -------

    The created project record as a dictionary

    """

    project = client.create(
        "/oteams/projects/",
        data={
            "organization": organization["id"],
            "name": project_name,
            "display_buildings": display_buildings,
            "comment": project_comment
        }
    )

    print(f"The project {project_name} has been successfully created")

    return project


def delete_project(
        client,
        project
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: dictionary
        project record
    """

    project = client.retrieve(
        "oteams/projects",
        project["id"]
    )

    if project is None:
        return

    client.destroy(
        "oteams/projects",
        project
    )

    print(f"The organization {project['name']} has been successfully deleted")