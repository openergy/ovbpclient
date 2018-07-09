import time
import datetime as dt

from openergy import get_client, get_odata_url


class ActivationMixin:

    activable_object_model = None
    activable_object_id = None

    def activate(self):

        client = get_client()

        client.detail_route(
            get_odata_url(self.activable_object_model),
            self.activable_object_id,
            "PATCH",
            "active",
            data={"value": True}
        )

    def deactivate(self):

        client = get_client()

        client.detail_route(
            get_odata_url(self.activable_object_model),
            self.activable_object_id,
            "PATCH",
            "active",
            data={"value": False}
        )
