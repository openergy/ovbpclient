class BaseModel:
    def __init__(self, endpoint, data):
        # touchy imports
        from ovbpclient.endpoints import BaseEndpoint
        self.endpoint: BaseEndpoint = endpoint
        self.client = self.endpoint.client
        self.data = data

    def __getattr__(self, item):
        if item not in self.data:
            raise AttributeError(f"{item} not found")
        return self.data[item]

    def __repr__(self):
        msg = f"<{self.endpoint.path}: "
        try:
            name = self.name
            msg += f"{name} ({self.id})>"
        except AttributeError:
            msg += f"{self.id}>"
        return msg

    def reload(self):
        reloaded_data = self.endpoint.client.rest_client.retrieve(self.endpoint.path, self.id)
        self.data = reloaded_data

    def update(self, **data):
        updated_data = self.endpoint.client.rest_client.partial_update(
            self.endpoint.path,
            self.id,
            data
        )
        self.data.update({k: updated_data[k] for k in data})

    def delete(self):
        self.endpoint.client.rest_client.destroy(
            self.endpoint.path,
            self.id
        )

    def detail_action(
            self,
            http_method,
            action_name,
            params=None,
            data=None,
            return_json=True,
            send_json=True):
        return self.client.rest_client.detail_action(
            self.endpoint.path,
            self.id,
            http_method,
            action_name=action_name,
            params=params,
            data=data,
            return_json=return_json,
            send_json=send_json
        )
