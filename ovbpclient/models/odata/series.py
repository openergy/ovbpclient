import warnings

import pandas as pd

from ..base import BaseModel


class Series(BaseModel):
    def select_data(
            self,
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
            return_se=True
    ):
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
        series_data = self.client.rest_client.detail_action(
            "odata/series",
            self.id,
            "get",
            "select",
            params=params
        )

        # see if response was cut (1e6 is max number of points return by backend)
        max_points_per_series = int(1e6)
        if len(series_data["index"]) == max_points_per_series:
            warnings.warn(
                "You requested more data than allowed on the platform (maximum number of points: 1.000.000).\n"
                f"This caused the series returned here to be cut to a maximum of {max_points_per_series} points.\n"
                "To get the full results, please launch an export (recommended) or split your current request into "
                "several smaller requests (query a smaller number of series at a time, "
                "or use the start and end arguments)",
                stacklevel=2
            )

        if not return_se:
            return series_data

        # parse to pandas series
        se = pd.Series(series_data["data"], series_data["index"])
        se.index = pd.to_datetime(se.index, unit="ms")
        return se
