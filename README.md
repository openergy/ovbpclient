# openergy

Client api to interact with openergy platform

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

## Suggested conda env

<pre>
openpyxl>=2.4.0,<2.0.0
requests>=2.11.1,<3.0.0
pandas>=0.16.2,<0.17
</pre>

## Releases

(p): patch, (m): minor, (M): major

### 2.0.2
* (m) pandas requirements were loosened

### 2.0.1
* (p): multiclean_config_model.xlsx added to MANIFEST.in

### 2.0.0
* (m): platform_to_excel added
* (M): cleaner batch_configure renamed to excel_to_platform
* (M): importer client kwarg removed
* (m): requests list_iter_all added
* (m): client management changed
* (m): util get_series_info added

### 1.0.0
* (m): list_iter_series created
* (M): first official release

### 0.3.0
* (m): client simplified
* (m): get_series_info added to api

### 0.2.0
* first referenced version