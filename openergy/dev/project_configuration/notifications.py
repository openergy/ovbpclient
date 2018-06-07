def get_notifications(
        client,
        project_odata_id=None,
        resource=None,
        resource_model=None,
        resolved=None
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project_odata_id: string
        The attribute "odata" of a project

    resolved: boolean
        get all resolved or unresolved notifications

    Returns
    -------

    The list of notifications of the project

    """

    params = {}

    if project_odata_id is not None:
        params["project"] = project_odata_id
    if resource is not None and resource_model is not None:
        params["source"] = f"{resource_model}:{resource['id']}"
    if resolved is not None:
        params["resolved"] = resolved

    notifications = client.list(
        "odata/notifications",
        params=params
    )["data"]

    return notifications


def update_notification(
        client,
        notification_resource,
        resolved=None
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    notification_resource: dictionary

    resolved: boolean
        update the resolved status of the notification

    Returns
    -------

    The updated notification

    """

    data = {}

    if resolved is not None:
        data["resolved"] = resolved

    return client.partial_update(
        "odata/notifications",
        notification_resource['id'],
        data=data
    )