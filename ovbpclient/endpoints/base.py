import ovbpclient
from ..queryset import Queryset
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
            filter_by=None,
            order_by=None
    ) -> Queryset:
        # todo: manage parameters
        params = dict(start=start, limit=limit)
        if filter_by is not None:
            # todo: code
            pass
        if order_by is not None:
            # todo: code
            pass
        data_l = self.client.rest_client.list(
            self.path,
            params=params
        )
        return Queryset([self.data_to_record(data) for data in data_l])

    def iter(self, filter_by=None, order_by=None):
        # todo: manage parameters
        limit = 200  # todo: check value
        i = 0
        for i in range(100):
            start = i * limit
            resources = self.list(
                start=start,
                limit=limit,
                filter_by=filter_by,
                order_by=order_by
            )
            if len(resources) == 0:
                break
            for resource in resources:
                yield resource
        else:
            raise RuntimeError(f"maximum iteration was reached ({i}), stopping")

    def list_all(self, filter_by=None, order_by=None) -> Queryset:
        return Queryset(self.iter(filter_by=filter_by, order_by=order_by))

    def create(self, data) -> "BaseModel":
        data = self.client.rest_client.create(self.path, data)
        return self.data_to_record(data)

    def retrieve(self, resource_id) -> "BaseModel":
        data = self.client.rest_client.retrieve(self.path, resource_id)
        return self.data_to_record(data)
