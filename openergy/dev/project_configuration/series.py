import pandas as pd

def get_single_series(
        client,
        project,
        generator_name,
        generator_model,
        series_name
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: dictionary
        Project record

    series_name: string
        The name of the series

    generator_name: string
        The name of the generator of the series

    generator_model: string
        "importer", "cleaner", "analysis"

    Returns
    -------

    The series record as a dictionary

    """

    series_record = client.list(
        "odata/series",
        params={
            "project": project["odata"],
            "name": series_name,
            "generator_name" : generator_name ,
            "generator_model": generator_model
        }
    )["data"]

    if len(series_record) ==0:
        print(f"Impossible to find the series {series_name} from {generator_model} {generator_name}")
    elif len(series_record) ==1:
        return series_record[0]
    else:
        print("Several series named {series_name} found, that's strange...")

    return


def get_series_of_generator(
        client,
        project,
        generator_name,
        generator_model
):
    """
    Parameters
    ----------

    client: RESTClient
        See openergy.set_client()

    project: dictionary
        Project record

    generator_name: string
        The name of the generator of the series

    generator_model: string
        "importer", "cleaner", "analysis"

    Returns
    -------

    The list of series records from the generator

    """

    return client.list(
        "odata/series",
        params={
            "project": project["odata"],
            "generator_name": generator_name,
            "generator_model": generator_model
        }
    )["data"]


def get_series_data(
        client,
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

    client: RESTClient
        See openergy.set_client()

    series: dictionary
        Series record

    start: string
        Date iso format

    end: string
        Date iso format

    dropna: Boolean

    closed: string
        "left", "right", "both"

    Returns
    -------

    Series data

    """

    series_pk_list = [se["otsdb_pk"] for se in series_list]

    params = {}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    if resample is not None:
        params["resample"] = resample
    if closed is not None:
        params["closed"] = closed

    series_data = client.list_route(
        "odata/series",
        "POST",
        "multi_select",
        params=params,
        data={"otsdb_pk": series_pk_list}
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
        return df