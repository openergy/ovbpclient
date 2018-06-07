def get_organization(client, organization_id):
    return client.retrieve(
        "oteams/organizations",
        organization_id
    )


def get_organization_from_name(client, organization_name):
    organization = client.list(
        "/oteams/organizations/",
        params={
            "name": organization_name
        }
    )["data"]

    if len(organization) == 0:
        print(f"No organization named {organization_name}")
        return
    elif len(organization) == 1:
        return organization[0]
    else:
        print(f"Several results found... Houston, we got a problem!")
        return


def create_organization(
        client,
        organization_name,
        organization_comment=""
):
    organization = client.create(
        "/oteams/organizations/",
        data={
            "name": organization_name,
            "comment": organization_comment
        }
    )

    print(f"The organization {organization_name} has been successfully created")

    return organization


def delete_organization(
        client,
        organization
):

    client.destroy(
        "oteams/organizations",
        organization["id"]
    )

    print(f"The organization {organization['name']} has been successfully deleted")