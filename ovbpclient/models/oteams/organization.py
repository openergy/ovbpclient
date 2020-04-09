from .. import BaseModel, oteams as oteams_models
from ...util import get_one_and_only_one


class Organization(BaseModel):
    def get_project(self, name) -> "oteams_models.Project":
        projects_l = self.client.projects.list(
            limit=2,
            filter_by=dict(name=name, organization=self.id))
        return get_one_and_only_one(projects_l)

    def create_project(self, name, comment=""):
        return self.client.projects.create(
            organization=self.id,
            name=name,
            comment=comment
        )
