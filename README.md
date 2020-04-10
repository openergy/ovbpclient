# ovbpclient

A python client to interact with Openergy Virtual Building Platform.

## Installation

    pip install ovbpclient
    
## Documentation

### Quickstart

[A detailed example with best practices is given here.](doc-users.md)

### User guide

**Note: the following user guide focuses on standard actions.**

**However, is often preferable to use shortcuts, when available, instead of standard actions. Many shortcuts
are given in the quickstart example.**

#### API documentation

To get a detailed documentation of the API, you may [directly connect to VBP backend](https://data.openergy.fr/api/v2) with your browser, log in, and navigate 
using the proposed links. On each page, you will find a ? on the upper right, you may click on it to view 
the documentation.

#### The client

The central object is the client. It contains:
- the target url
- the authentication credentials
- a list of all available endpoints (see bellow, chapter endpoints)
- shortcuts to access some records easily (get_organization, get_project, ...)

To initialize, your must provide credentials :

Prepare auth file:
    
    login
    password

Initialize client:

    from ovbpclient import Client
    
    # first method (auth_path is the path of a file containing login\npassword)
    client = Client(auth_path)
    
Instead of a path, you can give a buffer, which may be usefull if your credentials are in memory:

    # suppose my credentials are stored in two variables: login and password
    import io
    buffer= io.StringIO(f"{login}\n{password")
    client = Client(buffer)
    

#### Endpoints

Endpoints are the entry points to resources (comparable to tables in a relational database). They are attached to
the client. For example :
- projects: client.projects
- organizations: client.organizations
- gates: client.gates
- ...

Each endpoint contains:
- standard actions
- shortcuts to easily perform custom actions (varies for each endpoint)

**Standard endpoint actions:**

**list(start=0, limit=200, filter_by=None)**: returns a list of records (paginated).

    Starting from {start} record, in the limit of {limit} (the backend paginates records).
    You may filter these records if you provide a dictionary {filter_by} (filter_variable=filter_value, ...).
    Available filters are described in the backend API.
    
    Example:
        client.projects.list(filter_by=dict(organization=organization_id), limit=10)
    
**iter(filter_by=None)**: return an iterator of record elements.

    If you iter the reruned iterator, the client will automatically perform paginated querries until all the table 
    has been exhausted.
    This may for example be usefull if you want to iter records until you find one matching a specific condition, 
    then stop (which is more efficient than downloading all records).
    The filter system is available.
    
    Example:
        for project in client.projects.iter():
            if "energy" in project.name:
                break

**list_all(filter_by=None)**: returns a list of all records.

    The client performs multiple paginated requests, until all table has been exhausted.
    Should only be used when you known that there are not too many records.
    Filter system is available.
    
    Example:
        projects = client.projects.list_all(filter_by=dict(organization=organization_id))
    
**create(\*\*data)**: creates and returns a record.
    
    You must provide data containing record info.
    
    Example:
        project = client.project.create(organization=organization_id, name="project_name", comment="my comment")
        
        Note: it is easyier here to use the following shortcut:
        organization = client.get_organization("organization_name")
        project = organization.create_project("project_name", comment="my comment")
        
        
**retrieve(record_id)**: retrieves a record.

    You must provide record id.
    
    Example:
        project = client.project.retrieve("project_id")
        
        Note: it may be easyier here to use a shortcut (although less efficient in terms of number of requests).
        organization = client.get_organization("organization_name")
        project = organization.get_project("project_name")

**list_action(http_method, action_name, params=None, data=None, return_json=True, send_json=True)**: performs a custom action on enpoint

    This is an expert use of client, normally using proposed shortcuts should be sufficient.
    The available list actions are given in the backend API documentation.

#### Records

Records are the objects that are returned by endpoints queries.

A record contains:
- its data (stored in a dictionary: record.data). 
*The content of this dictionary is also available using getattr syntax (project.name for example, instead of project.data["name"])*
- standard record actions
- shortcuts


**Standard record actions:**

**reload()**: performs a request to reload data from api

    Example: series.reload()
    
    
**update(\*\*data)**: updates record data

    Example: project.update(comment="new comment")
    
**delete()**: deletes record

    Example: unitcleaner.delete()
    
**detail_action(http_method, action_name, params=None, data=None, return_json=True, send_json=True)**: 
performs a custom action on record

    This is an expert use of client, normally using proposed shortcuts should be sufficient.
    The available detail actions are given in the backend API documentation.
