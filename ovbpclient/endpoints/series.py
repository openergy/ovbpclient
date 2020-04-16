import os
import warnings
import contextlib
import tempfile
import zipfile
from typing import Iterable
import logging

import pandas as pd

from .base import BaseEndpoint
from ..models.odata import Series, Task

logger = logging.getLogger(__name__)


@contextlib.contextmanager
def _with_dir_path(dir_path=None):
    # prepare dir_path
    if dir_path is None:
        temp_dir = tempfile.TemporaryDirectory()
        dir_path = temp_dir.name
    else:
        temp_dir, dir_path = None, dir_path
    # call function
    try:
        yield dir_path
    finally:
        # cleanup
        if temp_dir is not None:
            temp_dir.cleanup()


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

    def export_data(
            self,
            series: Iterable[Series],
            start=None,
            end=None,
            out_freq=None,
            clock=None,
            out_mode="series",
            sep=",",
            decimal=".",
            time_grouper=None,
            with_tags=False,
            in_start_mode="right",
            in_end_mode="left"
    ):
        response_data = self.list_action(
            "post",
            "export",
            data=dict(
                series=[se.id for se in series],
                start=start,
                end=end,
                out_freq=out_freq,
                clock=clock,
                out_mode=out_mode,
                sep=sep,
                decimal=decimal,
                time_grouper=time_grouper,
                with_tags=with_tags,
                in_start_mode=in_start_mode,
                in_end_mode=in_end_mode
            )
        )
        return Task(self.client.series_export_tasks, response_data)

    def export_download_and_parse_data(
            self,
            series,
            download_dir_path=None,
            return_frame=True,
            start=None,
            end=None,
            out_freq=None,
            clock=None,
            out_mode="series",
            sep=",",
            decimal=".",
            time_grouper=None,
            with_tags=False,
            in_start_mode="right",
            in_end_mode="left"
    ):
        """
        Parameters
        ----------
        series
        download_dir_path
        return_frame
        start
        end
        out_freq
        clock
        out_mode
        sep
        decimal
        time_grouper
        with_tags
        in_start_mode
        in_end_mode

        Returns
        -------
        None or list of series or dataframe
        """
        # perform checks
        if not return_frame and download_dir_path is None:
            raise ValueError(
                "You asked not to return a frame, you must therefore provide a download directory "
                "(or else file will be downloaded in a temporary directory, which will be erased)."
            )
        if time_grouper is not None and return_frame:
            raise ValueError("You can't ask to return a frame if time_grouper is not None.")
        if with_tags and return_frame:
            raise ValueError("You can't aks to return a frame if with_tags is True.")
        if download_dir_path is not None and not os.path.exists(download_dir_path):
            raise NotADirectoryError(f"'{download_dir_path}' does not exist")

        # run export
        logger.info("Running export.")
        task = self.export_data(
            series,
            start=start,
            end=end,
            out_freq=out_freq,
            clock=clock,
            out_mode=out_mode,
            sep=sep,
            decimal=decimal,
            time_grouper=time_grouper,
            with_tags=with_tags,
            in_start_mode=in_start_mode,
            in_end_mode=in_end_mode
        )
        task.wait_for_completion()

        # retrieve ftp account
        me = self.client.users.retrieve("me")
        ftp_account = me.get_odata_ftp_account()

        # list directory
        entries = ftp_account.list_dir(path="series_exports")

        # filter and sort
        entries = sorted(filter(lambda x: x.type == "file", entries), key=lambda x: x.name, reverse=True)

        # check at least 1 record
        if len(entries) == 0:
            raise RuntimeError(
                "Did not find any export files although export was performed successfully. "
                "Something went wrong, can't continue."
            )
        entry = entries[0]

        # prepare local directory
        with _with_dir_path(dir_path=download_dir_path) as local_dir_path:
            # download file
            logger.info("Downloading export.")
            local_file_path = os.path.join(local_dir_path, entry.name)
            with ftp_account.get_ftputil_client() as ftputil_client:
                ftputil_client.download(entry.path, local_file_path)

            # unzip
            base_name, _ = os.path.splitext(entry.name)
            unzipped_dir_path = os.path.join(local_dir_path, base_name)
            with zipfile.ZipFile(os.path.join(local_dir_path, entry.name)) as zip_f:
                zip_f.extractall(unzipped_dir_path)

            # remove zipped file
            os.remove(local_file_path)

            # quit if frame not required
            if not return_frame:
                return

            # start parsing
            logger.info("Parsing files to frames.")

            # explore directory
            file_names = os.listdir(unzipped_dir_path)

            # empty directory
            if len(file_names) == 0:
                raise RuntimeError("Unzipped directory has no files, export did not return any data, aborting.")

            # check all files
            for name in file_names:
                _, ext = os.path.splitext(name)
                if ext != ".csv":
                    raise RuntimeError(f"Found a non csv file in unzipped directory ({name}), aborting.")

            # check mode
            if out_mode == "dataframe" and len(file_names) != 1:
                raise RuntimeError("Found more than one file in dataframe mode (which should not happen), aborting.")

            # prepare frames
            frames = []
            for name in file_names:
                frame = pd.read_csv(
                    os.path.join(unzipped_dir_path, name),
                    sep=sep,
                    decimal=decimal,
                    index_col=0,
                    parse_dates=True,
                    dtype=float
                )
                frame.index.name = None
                if out_mode == "series":
                    frame = frame.iloc[:, 0]
                    base_name, _ = os.path.splitext(name)
                    frame.name = base_name
                frames.append(frame)

            # return
            return frames[0] if out_mode == "dataframe" else frames
