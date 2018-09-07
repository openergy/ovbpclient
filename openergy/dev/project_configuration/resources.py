import time
import datetime as dt

from openergy import get_client, get_odata_url
from . import Organization, Project


class Resource:

    model = None

    def __init__(self, info):

        if ("id" in info.keys()) and ("name" in info.keys()):
            self._info = info
            self.__dict__.update(info)
        else:
            raise ValueError("The info must contain at least 'id' and 'name' field")

    @classmethod
    def retrieve(cls, model, organization_name=None, project_name=None, name=None, id=None):
        client = get_client()
        if id is None:
            if (organization_name is None) or (project_name is None) or (name is None):
                raise ValueError("Please indicate at least an id or an organization name, a project name "
                                 "and a resource name so that the resource can be retrieved")
            else:

                r = client.list(
                    get_odata_url(model),
                    params={
                        "name": name,
                        "project": Project.retrieve(organization_name, project_name).odata
                    }
                )["data"]

                if len(r) == 0:
                    print(f"No {model} named {name} found in the project {project_name} "
                          f"of organization {organization_name}")
                    return
                elif len(r) == 1:
                    id = r[0]["id"]

            info = client.retrieve(
                get_odata_url(model),
                id
            )

            return cls(info)

    def get_detailed_info(self):

        client = get_client()

        info = client.retrieve(
            get_odata_url(self.model),
            self.id
        )

        self._info = info
        self.__dict__.update(info)

        return self._info

    @property
    def info(self):
        return self._info

    def get_project(self):
        return Project.retrieve(odata=self.project)

    def get_organization(self):
        project = self.get_project()
        return Organization.retrieve(id=project.organization["id"])

    def delete(self):

        client = get_client()

        name = self.name

        client.destroy(
            get_odata_url(self.model),
            self.id
        )

        for k in self._info.keys():
            setattr(self, k, None)

        self._info = None

        print(f"The project {name} has been successfully deleted")