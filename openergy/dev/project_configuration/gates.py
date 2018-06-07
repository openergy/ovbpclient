from .resources_general import resource_already_exists, activate_resource

def create_internal_gate(
        client,
        project,
        gate_name,
        feeder_timezone,
        feeder_crontab,
        feeder_script,
        gate_comment="",
        replace=False,
        activate=True,
        passive=False
):
    if resource_already_exists(client, project, gate_name, "gate", replace):
        return

    print(f"Creation of gate {gate_name}")

    gate = client.create(
        "/odata/gates/",
        data={
            "project": project["odata"],
            "name": gate_name,
            "comment": gate_comment
        }
    )

    if not passive:

        client.detail_route(
            "odata/gate_ftp_accounts",
            gate["ftp_account"],
            "POST",
            "attach_new_oftp_account",
            data={}
        )

        base_feeder = client.create(
            "odata/base_feeders",
            data={
                "gate": gate["id"],
                "timezone": feeder_timezone,
                "crontab": feeder_crontab
            }
        )

        feeder = client.create(
            "odata/generic_basic_feeders",
            data={
                "base_feeder": base_feeder["id"],
                "script": feeder_script
            }
        )

        print(f"The feeder of gate {gate['name']} has been successfully created")

        if activate:
            activate_resource(client, base_feeder, "base_feeder")

    print(f"The gate {gate_name} has been successfully created")

    return gate


def create_external_gate(
        client,
        project,
        gate_name,
        ftp_host,
        ftp_port,
        ftp_protocol,
        ftp_login,
        ftp_password,
        gate_comment="",
        replace=False
):
    if resource_already_exists(client, project, gate_name, "gate", replace):
        return

    print(f"Creation of gate {gate_name}")

    gate = client.create(
        "/odata/gates/",
        data={
            "project": project["odata"],
            "name": gate_name,
            "comment": gate_comment
        }
    )

    ftp = client.partial_update(
        "odata/gate_ftp_accounts",
        gate["ftp_account"],
        data={
            "custom_host": ftp_host,
            "custom_port": ftp_port,
            "custom_protocol": ftp_protocol,
            "custom_login": ftp_login,
            "password": ftp_password
        }
    )

    print(f"The gate {gate_name} has been successfully created")

    return gate