from .. import BaseModel, oteams as oteams_models
from ...util import get_one_and_only_one


class Organization(BaseModel):
    def get_project_by_name(self, name) -> "oteams_models.Project":
        projects_qs = self.client.projects.list(
            limit=2,
            filter_by=dict(name=name, organization=self.id))
        return get_one_and_only_one(projects_qs)
