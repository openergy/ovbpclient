from ..endpoints import BaseEndpoint


class BaseModel:
    def __init__(self, endpoint: BaseEndpoint, data):
        self.endpoint = endpoint
        self.client = self.endpoint.client
        self.data = data

    def __getattr__(self, item):
        if item not in self.data:
            raise AttributeError(f"{item} not found")
        return self.data[item]

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.id}>"

    def reload(self):
        reloaded_data = self.endpoint.client.rest_client.retrieve(self.endpoint.path, self.id)
        self.data = reloaded_data

    def update(self, **data):
        updated_data = self.endpoint.client.rest_client.partial_update(
            self.endpoint.path,
            self.id,
            data
        )
        self.data = updated_data  # todo: check that partial update returns complete data

    def delete(self):
        self.endpoint.client.rest_client.destroy(
            self.endpoint.path,
            self.id
        )


class ActiveBaseModel(BaseModel):
    def activate(self):
        self.endpoint.client.rest_client.detail_action(
            self.endpoint,
            self.id,
            "patch",
            "active",
            data=dict(value=True)
        )

    def deactivate(self):
        self.endpoint.client.rest_client.detail_action(
            self.endpoint,
            self.id,
            "patch",
            "active",
            data=dict(value=False)
        )
