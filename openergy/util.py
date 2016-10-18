import pandas as pd

from openergy import client


def select_series(uuid, **select_kwargs):
    """
    Parameters
    ----------
    uuid: series_id or (project_name, generator_model, generator_name, name)
    """
    # get id
    if isinstance(uuid, (tuple, list)):
        project_name, generator_model, generator_name, name = uuid
        all_series = client.list(
            "opmeasures/series",
            params=dict(
                project_name=project_name,
                generator_model=generator_model,
                generator_name=generator_name,
                name=name
            ))
        assert len(all_series["data"]) == 1, "Request did not return one and only one element: %s" % pprint.pformat(
            all_series["data"])
        series_id = all_series["data"][0]["id"]
    else:
        series_id = uuid
        all_series = client.list(
            "opmeasures/series",
            params=dict(
                id=uuid
            ))
        assert len(all_series["data"]) == 1, "Request did not return one and only one element: %s" % pprint.pformat(
            all_series["data"])
        name = all_series['data'][0]['name']

    # select data
    rep = client.detail_route("opmeasures/series", series_id, "GET", "select", params=select_kwargs, return_json=False)

    # transform to pandas series
    se = pd.read_json(rep, orient="split", typ="series")

    # put correct name
    se.name = series_id if name is None else name

    return se
