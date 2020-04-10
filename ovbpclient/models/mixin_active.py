class ActiveModelMixin:
    def activate(self):
        self.detail_action(
            "patch",
            "active",
            data=dict(value=True)
        )

    def deactivate(self):
        self.detail_action(
            "patch",
            "active",
            data=dict(value=False)
        )
