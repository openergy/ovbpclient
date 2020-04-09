from typing import List
from ovbpclient.models import odata as odata_models


class GeneratorModelMixin:
    def list_all_output_series(self) -> List["odata_models.Series"]:
        return self.client.series.list_all(filter_by=dict(generator=self.id))
