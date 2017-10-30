# openergy

Client api to interact with openergy platform

## Suggested conda env

<pre>
openpyxl>=2.4.7,<3.0.0
requests>=2.14.2,<3.0.0
nose>=1.3.7,<2.0.0
pandas>=0.20.1,<0.21.0
pytables>=3.2.0,<4.0
</pre>

## Url endpoints philosophy

Mainly inspired by [rest_framework simple router actions](http://www.django-rest-framework.org/api-guide/routers/#simplerouter). 



## Examples

<pre>
from openergy import set_client, select_series
client = set_client("login", "password", "host")
</pre>


### select series
<pre>
# returns a pandas Series object
se = select_series("993e2f73-20ef-4f60-8e06-d81d6cefbc9a")
</pre>


### create local database
<pre>
from openergy import LocalDatabase

db = LocalDatabase(db_dir_path)

# download one series

# (local_se is not a pandas series but a local database series object)
local_se = db.get_local_series(
    "my_project",
    "analysis",  # importer, cleaner or analysis
    "my_analysis",
    "se1")
local_se.download()

# se1 is a pandas series
se1 = local_se.data

# download multiple series
db.download_all_series(
    my_project,
    generator_model=analysis,  # importer, cleaner or analysis
    generator_name=my_analysis)
# 1. local se1 will be deleted and downloaded again
# 2. all project will be downloaded if no generator has been specified

# work with series
se1 = db.get_local_series(
    "my_project",
    "analysis",
    "my_analysis",
    "se1").data
</pre>
