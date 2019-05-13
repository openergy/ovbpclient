import warnings

import pandas as pd

from openergy import get_client


def get_series_data(
    series_list,
    return_df=True,
    start=None,
    end=None,
    resample=None,
    dropna=None,
    closed=None
):
    """
    Parameters
    ----------

    series_list: list of Series instances

    start: string
        Date iso format

    end: string
        Date iso format

    dropna: Boolean

    closed: string
        "left", "right", "both"

    resample: string


    Returns
    -------

    Series data

    """

    client = get_client()

    series_pk_list = [se.otsdb_pk for se in series_list]

    params = {}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    if resample is not None:
        params["resample"] = resample
    if closed is not None:
        params["closed"] = closed
    if dropna:
        params["dropna"] = True

    # This is the maximum number of points the API will return per series
    max_points_per_series = int(1e6) // len(series_pk_list)

    series_data = client.list_route(
        "odata/series",
        "POST",
        "multi_select",
        params=params,
        data={"otsdb_pk": series_pk_list}
    )
    cut = False
    for se_dict in series_data.values():
        if len(se_dict["index"]) == max_points_per_series:
            cut = True
    if cut:
        warnings.warn(
            "You requested more data than allowed on the platform (maximum number of points: 1.000.000).\n"
            f"This caused the series returned here to be cut to a maximum of {max_points_per_series} points.\n"
            "To get the full results, please launch an import (recommended) or split your current request into "
            "several smaller requests (query a smaller number of series at a time, or use the start and end arguments)",
            stacklevel=2
        )

    if not return_df:
        return series_data
    else:
        df_data = {}
        for pk, se_dict in series_data.items():
            se = pd.Series(se_dict["data"], se_dict["index"])
            df_data[se_dict["name"]] = se
        df = pd.DataFrame(df_data)
        df.index = pd.to_datetime(df.index, unit='ms')
        if len(df.columns) == 1:
            return df[df.columns[0]]
        return df


class Series:

    def __init__(self, info):

        if ("id" in info.keys()) and ("name" in info.keys()):
            self._info = info
            self.__dict__.update(info)
        else:
            raise ValueError("The info must contain at least 'id' and 'name' field")

    @classmethod
    def retrieve(
            cls,
            project_name=None,
            generator_name=None,
            generator_model=None,
            name=None,
            id=None
    ):
        client = get_client()
        if id is None:
            if (name is None) or (project_name is None)\
                    or (generator_name is None) or (generator_model) is None:
                raise ValueError("Please indicate at least an id or a project name, a generator name, a generator model"
                                 " and a name so that the series can be retrieved")
            else:
                r = client.list(
                    "odata/series",
                    params={
                        "name": name,
                        "project_name": project_name,
                        "generator_name": generator_name,
                        "generator_model": generator_model
                    }
                )["data"]

                if len(r) == 0:
                    return
                elif len(r) == 1:
                    id = r[0]["id"]

        info = client.retrieve(
            "odata/series",
            id
        )

        return cls(info)

    def get_data(
        self,
        return_df=True,
        start=None,
        end=None,
        resample=None,
        dropna=None,
        closed=None
    ):

        return get_series_data(
            [self],
            return_df,
            start,
            end,
            resample,
            dropna,
            closed
        )
