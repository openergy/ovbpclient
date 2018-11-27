from openergy import get_client, get_full_list


class Organization:

    def __init__(self, info):
        """

        Parameters
        ----------
        info: dictionary
            A dict that contains at least id and name as keys
        """

        if ("id" in info.keys()) and ("name" in info.keys()):
            self._info = info
            self.__dict__.update(info)
        else:
            raise ValueError("The info must contain at least 'id' and 'name' field")

    @classmethod
    def retrieve(cls, name=None, id=None):
        """
        Retrieve organization detailed info and create Organization instance from this info.
        The name or the id is enough, don't need both

        Parameters
        ----------
        name: string
            The name of the organization.

        id: uuid string
            The id of the organization

        Returns
        -------
        
        The Organization instance.

        """

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
        """

        Returns
        -------

        A dictionary that contains all info about the Organization

        """

        client = get_client()

        info = client.retrieve(
            "oteams/organizations",
            self.id
        )
        self._info = info
        self.__dict__.update(info)

        return self._info

    def delete(self):
        """
        You must be super Admin with can_delete right

        """
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
        """
        Retrieve a project within the Organization
        
        Parameters
        ----------
        project_name: string 

        Returns
        -------
        
        The Project Instance
        """

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
            print(f"No project named {project_name} in organization {self.name}")
            return
            # raise ValueError(f"No project named {project_name} in organization {self._info.name}")
        else:
            return Project(r[0])

    def create_project(
            self,
            project_name,
            project_comment="",
            display_buildings=True,
            replace=False
    ):
        """

        You must have creation rights within the organization

        Parameters
        ----------
        project_name: string

        project_comment: string

        display_buildings: bool

        replace: bool
            replace by a new one if a project with the same name already exists

        Returns
        -------

        """

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

        project_created = Project(new_project_info)
        project_created.get_detailed_info()
        return project_created

    def get_all_projects(self):
        """

        Returns
        -------

        The list of all projects (as Project instances) within the Organization.

        """

        r = get_full_list(
            "oteams/projects",
            params={
                "organization":self.id
            }
        )

        # Touchy import
        from . import Project

        return [Project(info) for info in r]


def create_organization(name):
    """
    You must have super admin rights can_create_organization

    Parameters
    ----------
    name: string

    Returns
    -------

    The instance of the Organization just created

    """
    client = get_client()
    r = client.create(
        "oteams/organization",
        data={
            "name":name
        }
    )
    return Organization(r)


def get_my_organizations():
    """

    Returns
    -------

    All the organizations you belong to

    """
    r = get_full_list(
        "oteams/organizations"
    )
    return [Organization(org_info) for org_info in r]
