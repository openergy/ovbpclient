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

### 0.3.0
* (m): client simplified
* (m): get_series_info added to api

### 0.2.0
* first referenced version