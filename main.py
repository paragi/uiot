import json
import urllib.request
from pprint import pprint
import requests
from datetime import datetime

def test1():
    # Constructing more specific searches seems to require authorisation
    url = 'https://api.energidataservice.dk/datastore_search?resource_id=elspotprices'
    fileobj = urllib.request.urlopen(url)
    elspotprice_dict = json.loads(fileobj.read())
    print(json.dumps(elspotprice_dict, indent=2))

def test2():
    query = '''
    SELECT COUNT(*) 
        AS cnt, to_char(date_trunc('day', "HourUTC"), 'yyyy-mm-dd')
        AS dc
    FROM "fcrreservesdk1"
    WHERE "HourUTC" > ((current_timestamp at time zone 'UTC') - INTERVAL '30 days')
    GROUP BY date_trunc('day', "HourUTC")
    ORDER BY date_trunc('day', "HourUTC")
    '''
    uri = "https://api.energidataservice.dk/datastore_search_sql?sql="
    fileobj = urllib.request.urlopen(uri + requests.utils.quote(query))
    elspotprice_dict = json.loads(fileobj.read())
    print(json.dumps(elspotprice_dict, indent=2))

def test3():
    #ChargeOwner GLN_Number ChargeType ChargeTypeCode Note Description ValidFrom ValidTo VATClass Price1 Price2 Price3 Price4 Price5 Price6 Price7 Price8 Price9 Price10 Price11 Price12 Price13 Price14 Price15 Price16 Price17 Price18 Price19 Price20 Price21 Price22 Price23 Price24 TransparentInvoicing TaxIndicator ResolutionDuration

    query = '''
    SELECT * 
    FROM "datahubpricelist"
    WHERE "ValidFrom" >= NOW()
    ORDER BY "ValidFrom" desc
    '''
    uri = "https://api.energidataservice.dk/datastore_search_sql?sql="
    fileobj = urllib.request.urlopen(uri + requests.utils.quote(query))
    elspotprice_dict = json.loads(fileobj.read())
    print(json.dumps(elspotprice_dict, indent=2))

def charge_owners():
    query = '''
    SELECT DISTINCT "ChargeOwner" 
    FROM "datahubpricelist"
    ORDER BY "ChargeOwner"
    '''
    uri = "https://api.energidataservice.dk/datastore_search_sql?sql="
    fileobj = urllib.request.urlopen(uri + requests.utils.quote(query))
    result_dict = json.loads(fileobj.read())
    print(json.dumps(result_dict, indent=2))

class SpotPrice:
    # Retrieve dataset from SQL query with energi data service
    # See https://www.energidataservice.dk for details
    def get_energidataservice(self, query: object) -> object:
        uri = "https://api.energidataservice.dk/datastore_search_sql?sql="
        #print("Get:", uri + query)
        fileobj: object = urllib.request.urlopen(uri + requests.utils.quote(query.strip()))
        result_dict = json.loads(fileobj.read())
        return result_dict

    # Get list of Price Area names
    def areas(self):
        query = '''
            SELECT DISTINCT "PriceArea" 
            FROM "elspotprices"
            ORDER BY "PriceArea"
            '''
        result = self.get_energidataservice(query)
        return [li["PriceArea"] for li in [*result["result"]["records"]]]

    # Get listy of current and future spot price
    def prices(self, price_area):
        query = '''
            SELECT "PriceArea", "HourDK", "SpotPriceDKK"
            FROM "elspotprices"
            WHERE "HourDK" >= NOW()
            ORDER BY "PriceArea", DATE_TRUNC('hour', "HourDK")
            '''
        result = self.get_energidataservice(query)
        # Format dictionary

        price_list = {}
        for entry in [*result["result"]["records"]]:
            time = datetime.strptime(entry["HourDK"], '%Y-%m-%dT%H:%M:%S').hour
            if entry["PriceArea"] not in price_list: price_list[entry["PriceArea"]] = {}
            price_list[entry["PriceArea"]][datetime.strptime(entry["HourDK"], '%Y-%m-%dT%H:%M:%S').hour] = round(entry["SpotPriceDKK"]/1000,2)

        if price_area is not None:
            if price_list[price_area] is not None:
                return price_list[price_area]
            else:
                return None
        else:
            return price_list


spot_price = SpotPrice()
print(spot_price.areas())
pprint(spot_price.prices("DK2"))

