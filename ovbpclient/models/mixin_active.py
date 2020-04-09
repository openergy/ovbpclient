class ActiveModelMixin:
    def activate(self):
        self.endpoint.client.rest_client.detail_action(
            self.endpoint.path,
            self.id,
            "patch",
            "active",
            data=dict(value=True)
        )

    def deactivate(self):
        self.endpoint.client.rest_client.detail_action(
            self.endpoint.path,
            self.id,
            "patch",
            "active",
            data=dict(value=False)
        )
