# ovbpclient

A python client to interact with Openergy Virtual Building Platform.

## Installation

    conda install ovbpclient
    
or
    
    pip install ovbpclient
    
## example

pass.txt:

    login
    password

script example:
    
    from ovbpclient import Client
    
    client = Client(auth_buffer_or_path="pass.txt")
    
    organization = client.get_organization("Organization name")
    print(organization)
    
    debug = organization.get_project("Project name")
    print(debug)
    
    print("\ngates")
    for gate in debug.list_all_gates():
        print(f"  {gate}")
    
    print("\nimporters:")
    for importer in debug.list_all_importers():
        print(f"  {importer}")
    
    print("\ncleaners")
    for cleaner in debug.list_all_cleaners():
        print(f"  {cleaner}")
    
    print("\nanalyses")
    for analysis in debug.list_all_analyses():
        print(f"  {analysis}")
    
    print("\nnotifications")
    for notification in debug.list_all_notifications():
        print(f"  {notification}")
