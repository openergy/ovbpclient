import time
import datetime as dt

resource_urls = {
    "gate":"odata/gates",
    "base_feeder":"odata/base_feeders",
    "importer": "odata/importers",
    "cleaner": "odata/cleaners",
    "unitcleaner": "odata/unitcleaners",
    "analysis": "odata/analyses",
    "analysis_input": "odata/analysis_inputs",
    "analysis_output": "odata/analysis_outputs",
}



def get_resource(
    client,
    resource_id,
    resource_model
):
    return client.retrieve(
        resource_urls[resource_model],
        resource_id
    )


def get_resource_from_name(
        client,
        project,
        resource_name,
        resource_model
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: dictionary
        project record

    resource_name: string
        The name of the resource

    resource_model: string
        "gate", "importer", "cleaner" or "analysis"

    Returns
    -------

    The resource as a dictionary
    """

    resource = client.list(
        f"/{resource_urls[resource_model]}/",
        params={
            "name": resource_name,
            "project": project["odata"]
        }
    )["data"]

    if len(resource) == 0:
        print(f"No {resource_model} {resource_name} found")
        return
    else:
        return resource[0]


def activate_resource(
        client,
        resource,
        resource_model
):
    """
    Activate a resource (trun On). Available for Gates, Importers, Basefeeders and Analyses.

    Parameters
    ----------

    client: RESTClient
    See openergy.set_client()

    resource: dictionary

    resource_model: string
        "base_feeder", "importer", "unitcleaner" , "analysis"

    """

    if "name" in resource.keys():
        resource_name = resource['name']
    else:
        resource_name = resource['id']

    print(f"Activation of {resource_model} {resource_name}")

    client.detail_route(
        resource_urls[resource_model],
        resource["id"],
        "PATCH",
        "active",
        data={"value": True}
    )

    print(f"The {resource_model} {resource_name} has been successfully activated \n")


def deactivate_resource(
        client,
        resource,
        resource_model
):
    """
    Deactivate a resource (trun Off). Available for Gates, Importers, Basefeeders and Analyses.

    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    resource: dictionary

    resource_model: string
        "base_feeder", "importer", "unitcleaner" , "analysis"

    """

    if "name" in resource.keys():
        resource_name = resource['name']
    else:
        resource_name = resource['id']

    print(f"Deactivation of {resource_model} {resource_name}")

    client.detail_route(
        resource_urls[resource_model],
        resource["id"],
        "PATCH",
        "active",
        data={"value": False}
    )

    print(f"The {resource_model} {resource_name} has been successfully deactivated")


def delete_resource(
        client,
        resource,
        resource_model
):
    if resource_model in ["gate", "importer", "unitcleaner", "analysis"]:
        deactivate_resource(
            client,
            resource,
            resource_model
        )

    if (resource_model != "gate"):
        client.detail_route(
            resource_urls[resource_model],
            resource["id"],
            "POST",
            "action",
            data={"name": "clear"}
        )

    client.destroy(
        resource_urls[resource_model],
        resource["id"]
    )

    print(f"The {resource_model} {resource['name']} has been successfully deleted")


def delete_resource_by_name(
        client,
        project,
        resource_name,
        resource_model
):
    resource = client.list(
        resource_urls[resource_model],
        params={
            "name": resource_name,
            "project": project["odata"]
        }
    )["data"]

    if len(resource) == 0:
        print(f"No {resource_model} named {resource_name} can be found")

    if len(resource) == 1:

        delete_resource(
            client,
            resource[0],
            resource_model
        )

    else:
        print(f"Several resources found for {resource_model} {resource_name}, that's strange...")


def resource_already_exists(
        client,
        project,
        resource_name,
        resource_model,
        replace
):
    """

    Check if a resource already exists.

    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: dictionary (project record)
        The attribute "odata" of a project

    resource_name: string
        The name of the resource

    resource_model: string
        "gate", "importer", "cleaner" or "analysis"

    replace: boolean
        False -> The resource is not deleted if it exists already
        True -> The resource get deleted if it exists already

    Returns
    -------

    A boolean.
        True -> The resource existed already and still exists
        False -> The resource did not exist or has been deleted (if replace=True)
    """

    resource = client.list(
        resource_urls[resource_model],
        params={
            "name": resource_name,
            "project": project["odata"]
        }
    )["data"]

    if len(resource) == 0:
        return False

    if len(resource) == 1 and replace:

        delete_resource(
            client,
            resource[0],
            resource_model
        )
        return False

    elif len(resource) > 0 and not replace:
        print(f"The {resource_model} {resource_name} already exists, use replace=True to overwrite it")
        return True

    else:
        print(f"Several resources found")
        return True


def waiting_for_outputs(
        client,
        generator,
        generator_model,
        outputs_length,
        sleep_loop_time=30,
        abort_time=180
):
    """
    Waiting for the outputs of a resource to be created

    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    generator: dictionary

    generator_model: string
        "gate", "importer", "base_feeder", "analysis"

    outputs_length: int
        The expected number of outputs

    sleep_loop_time: int
        The time to wait between each outputs number check in seconds

    abort_time: int
        The maximum time to wait

    """

    print(f"Waiting for outputs of {generator_model} {generator['name']}")

    outputs_ready = False
    start_time = dt.datetime.now()

    while not outputs_ready:

        if (dt.datetime.now() - start_time) < abort_time :

            print('...')
            time.sleep(sleep_loop_time)

            outputs = client.list(
                "odata/series",
                params={
                    "generator": generator["id"]
                }
            )["data"]

            print(f"{len(outputs)} outputs generated over {outputs_length} expected")

            if len(outputs) == outputs_length:
                outputs_ready = True
                print(f"Outputs of {generator_model} {generator['name']} are ready \n\n")
                return

        else:
            print("Abort time exceeded. Exit")
            return