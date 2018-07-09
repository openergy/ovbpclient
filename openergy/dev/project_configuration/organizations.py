from openergy import get_client, is_uuid


def create_organization(name):
    client = get_client()
    new_org_info = client.create(
        "oteams/organization",
        data={
            "name":name
        }
    )
    return new_org_info


class Organization:

    def __init__(self, info):

        if ("id" in info.keys()) and ("name" in info.keys()):
            self._info = info
            self.__dict__.update(info)
        else:
            raise ValueError("The info must contain at least 'id' and 'name' field")

    @classmethod
    def retrieve(cls, name=None, id=None):
        client = get_client()

        if id is None:
            if name is None:
                raise ValueError("Please indicate at least a name or an id so that the organization can be retrieved")
            else:
                r = client.list(
                    "oteams/organizations/",
                    params={
                        "name": name
                    }
                )["data"]

                if len(r) == 0:
                    return
                elif len(r) == 1:
                    id = r[0]["id"]

        info = client.retrieve(
            "oteams/organizations",
            id
        )

        return cls(info)

    def get_detailed_info(self):

        client = get_client()

        info = client.retrieve(
            "oteams/organizations",
            self.id
        )
        self._info = info
        self.__dict__.update(info)

        return self._info

    def delete(self):

        # You must be super Admin with can_delete right

        name = self.name

        client = get_client()

        client.destroy(
            "oteams/organizations",
            self.id
        )

        for k in self._info.keys():
            setattr(self, k, None)

        self._info = None

        print(f"The organization {name} has been successfully deleted")

    def get_project(self, project_name):

        # Touchy import
        from . import Project

        client = get_client()

        r = client.list(
            "oteams/projects",
            params={
                "organization": self.id,
                "name": project_name
            }
        )["data"]

        if len(r) == 0:
            return
        else:
            return Project(r[0])

    def create_project(
            self,
            project_name,
            project_comment="",
            display_buildings=True,
            replace=False
    ):

        # Touchy import
        from . import Project

        client = get_client()

        # verify if project already exists
        p = self.get_project(project_name)
        if p is not None:
            print(f"Project {project_name} already existed")
            if not replace:
                return
            else:
                print(f"Deleting current project {project_name}")
                p.delete()

        print(f"Creating new project {project_name}")

        new_project_info = client.create(
            "oteams/projects",
            data={
                "organization": self.id,
                "name": project_name,
                "comment": project_comment,
                "display_buildings": display_buildings
            }
        )

        print(f"The project {project_name} has been successfully created")

        return Project(new_project_info)

    def get_all_projects(self):

        client = get_client()

        r = client.list(
            "oteams/projects",
            params={
                "organization":self.id
            }
        )["data"]

        # Touchy import
        from . import Project

        return [Project(info) for info in r]