import pprint

import pandas as pd
from uuid import UUID

from openergy import get_client


def is_uuid(uuid):
    if isinstance(uuid, str):
        try:
            uid = UUID(uuid)
            return uid.hex == uuid.replace('-', '')
        except ValueError:
            return False

    return False


def get_odata_url(record):
    if record == "analysis":
        return "odata/analyses"
    else:
        return f"odata/{record}s"


def get_full_list(url, params={}):  # todo: this dict shouldn't be here...
    client = get_client()

    def get_data(start, full_list):
        params["start"] = start
        r = client.list(
            url,
            params=params
        )["data"]

        # from pprint import pprint
        # print("url", url)
        # print("params")
        # pprint(params)
        # print("r")
        # pprint(r)

        if len(r) == 0:
            return full_list

        full_list += r
        return get_data(start + len(r), full_list)

    _full_list = []
    return get_data(0, _full_list)


def get_series_info(uuid, detailed=True):
    """
    Returns
    -------
    info: comes from list view, not detailed
    """
    client = get_client()

    flat_info = None

    # project_name, generator_model, generator_name, name => retrieve flat info and series_id
    if isinstance(uuid, (tuple, list)):
        project_name, generator_model, generator_name, name = uuid
        all_series = client.list(
            "odata/series",
            params=dict(
                project_name=project_name,
                generator_model=generator_model,
                generator_name=generator_name,
                name=name
            ))
        assert len(all_series["data"]) == 1, "Request did not return one and only one element: %s" % pprint.pformat(
            all_series["data"])
        flat_info = all_series["data"][0]

        # detailed
        series_id = all_series["data"][0]["id"]
    else:
        series_id = uuid

    # detailed route
    if detailed:
        detailed_info = client.retrieve("odata/series", series_id)
        return detailed_info

    # not detailed
    if flat_info is None:
        all_series = client.list(
            "odata/series",
            params=dict(
                id=uuid
            ))
        assert len(all_series["data"]) == 1, "Request did not return one and only one element: %s" % pprint.pformat(
            all_series["data"])
        flat_info = all_series['data'][0]
    return flat_info


def select_series(uuid, **select_kwargs):
    """
    Parameters
    ----------
    uuid: series_id or (project_name, generator_model, generator_name, name)
    """
    client = get_client()

    # get id and name
    info = get_series_info(uuid)
    series_id, name = info["id"], info["name"]

    # select data
    rep = client.detail_action("odata/series", series_id, "GET", "select", params=select_kwargs, return_json=False)

    # transform to pandas series
    se = pd.read_json(rep, orient="split", typ="series")

    # put correct name
    se.name = series_id if name is None else name

    return se

