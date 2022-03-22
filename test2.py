import json
import requests
query = {"query":"query Dataset {elspotprices(where: {HourUTC: {_gte: \"2022-03-22\", _lt: \"2022-03-25\"}PriceArea: {_eq: \"DK2\"}} order_by: {HourDK: desc} limit: 100 offset: 0){HourUTC HourDK PriceArea SpotPriceDKK SpotPriceEUR }}"}
url = 'https://api.energidataservice.dk/datastore_search?resource_id=elspotprices&limit=5'

r = request.post('https://api.energidataservice.dk/datastore_search', json=query)
print(r)

