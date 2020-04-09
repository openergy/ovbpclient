import warnings
from typing import Iterable

import pandas as pd

from .base import BaseEndpoint
from ..models.odata import Series


class SeriesEndpoint(BaseEndpoint):
    def select_data(
            self,
            series: Iterable[Series],
            start=None,
            end=None,
            resample=None,
            dropna=None,
            closed=None,
            resample_rule=None,
            convention=None,
            start_mode=None,
            utc_now=None,
            max_acceptable_delay=None,
            max_rows_nb=None,
            clock=None,
            with_tags=None,
            unfilter=None,
            return_df=True
    ):
        # prepare tsdb pks
        otsdb_pks = [se.otsdb_pk for se in series]

        # check not empty
        if len(otsdb_pks) == 0:
            raise ValueError("series must at least contain one series, none was found")

        # prepare params
        params = dict()
        for k in (
                "start",
                "end",
                "resample",
                "dropna",
                "closed",
                "resample_rule",
                "convention",
                "start_mode",
                "utc_now",
                "max_acceptable_delay",
                "max_rows_nb",
                "clock",
                "with_tags",
                "unfilter"
        ):
            v = locals()[k]
            if v is not None:
                params[k] = v

        # perform request
        series_data = self.client.rest_client.list_action(
            "odata/series",
            "post",
            "multi_select",
            params=params,
            data={"otsdb_pk": otsdb_pks}
        )

        # see if response was cut (1e6 is max number of points return by backend)
        max_points_per_series = int(1e6) // len(otsdb_pks)
        for se_dict in series_data.values():
            if len(se_dict["index"]) == max_points_per_series:
                warnings.warn(
                    "You requested more data than allowed on the platform (maximum number of points: 1.000.000).\n"
                    f"This caused the series returned here to be cut to a maximum of {max_points_per_series} points.\n"
                    "To get the full results, please launch an export (recommended) or split your current request into "
                    "several smaller requests (query a smaller number of series at a time, "
                    "or use the start and end arguments)",
                    stacklevel=2
                )
                break

        if not return_df:
            return series_data

        # parse to data frame
        df_data = {}
        for pk, se_dict in series_data.items():
            se = pd.Series(se_dict["data"], se_dict["index"])
            df_data[se_dict["name"]] = se
        df = pd.DataFrame(df_data)
        df.index = pd.to_datetime(df.index, unit='ms')
        return df
