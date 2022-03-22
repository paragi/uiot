import json
import urllib.request

url = 'https://api.energidataservice.dk/datastore_search?resource_id=elspotprices&limit=5'
fileobj = urllib.request.urlopen(url)
elspotprice_dict=json.loads(fileobj.read())
print(json.dumps(elspotprice_dict,indent=2))

