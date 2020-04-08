import ovbpclient
from ..models import BaseModel


class BaseEndpoint:
    def __init__(self, client: "ovbpclient.Client", path, model_cls=None):
        self.path = path
        self.client = client
        self.model_cls = BaseModel if model_cls is None else model_cls

    def __repr__(self):
        return f"<{self.path}>"

    def data_to_record(self, data):
        return self.model_cls(self, data)

    def list(
            self,
            start=0,
            limit=200,
            filter_by=None
    ) -> list:
        """
        Parameters
        ----------
        start: int, default 0
            start with the record at given position
        limit: int, default 200
            maximum number of returned records (backend won't return more than 200)
        filter_by: dict
            {parameter: value to filter by, ...}
        Returns
        -------
        list
        """
        params = dict(start=start, length=limit)
        if filter_by is not None:
            params.update(filter_by)
        data_l = self.client.rest_client.list(
            self.path,
            params=params
        )["data"]
        return [self.data_to_record(data) for data in data_l]

    def iter(self, filter_by=None):
        limit = 200
        i = 0
        for i in range(100):
            start = i * limit
            resources = self.list(
                start=start,
                limit=limit,
                filter_by=filter_by
            )
            if len(resources) == 0:
                break
            for resource in resources:
                yield resource
        else:
            raise RuntimeError(f"maximum iteration was reached ({i}), stopping")

    def list_all(self, filter_by=None) -> list:
        return list(self.iter(filter_by=filter_by))

    def create(self, data) -> "BaseModel":
        data = self.client.rest_client.create(self.path, data)
        return self.data_to_record(data)

    def retrieve(self, resource_id) -> "BaseModel":
        data = self.client.rest_client.retrieve(self.path, resource_id)
        return self.data_to_record(data)
