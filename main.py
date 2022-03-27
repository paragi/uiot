import json
import urllib.request
from pprint import pprint
from typing import Any
import textgraph
import requests

# Local modules
from timestamp import *

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
    # ChargeOwner GLN_Number ChargeType ChargeTypeCode Note Description ValidFrom ValidTo VATClass Price1 Price2 Price3 Price4 Price5 Price6 Price7 Price8 Price9 Price10 Price11 Price12 Price13 Price14 Price15 Price16 Price17 Price18 Price19 Price20 Price21 Price22 Price23 Price24 TransparentInvoicing TaxIndicator ResolutionDuration

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
    def __init__(self):
        self._price_list: dict[Any, Any] = {}
        self.update_time: datetime = datetime.min
        self.success: bool = False

    # Retrieve dataset from SQL query with energi data service
    # See https://www.energidataservice.dk for details
    # Issues with:
    #   price in DKK missing at times
    #   HourDK summertime not always corrected.
    #   SQL capabilities very limited
    # Use UTC and price in EUR

    def get_energidataservice(self, query: object) -> object:
        uri = "https://api.energidataservice.dk/datastore_search_sql?sql="
        # print("Get:", uri + query)
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

    # Get current spot price list, from now
    # Creates a list of price areas, containing lists of time tags and spot price
    def update_price_list(self):
        query = '''
                        SELECT "PriceArea", "HourUTC", "SpotPriceEUR"
                        FROM "elspotprices"
                        WHERE "HourUTC" >= NOW()
                        ORDER BY "PriceArea", "HourUTC"
                        '''
        result = self.get_energidataservice(query)
        # pprint(result)
        # print("Updating price list")
        if result['success']:
            self._price_list = {}

            for entry in result["result"]["records"]:
                try:
                    if not entry["PriceArea"] in self._price_list:
                        self._price_list[entry["PriceArea"]] = {}
                    # print(entry)

                    timestamp = Timestamp(entry["HourUTC"], '%Y-%m-%dT%H:%M:%S%z')
                    price = round(float(entry["SpotPriceEUR"]) / 1000, 3)
                    self._price_list[entry["PriceArea"]][timestamp] = price
                    # print(entry,timestamp, price)

                except Exception as e:
                    pass

        # self.prune_price_list()
        # print(self._price_list)
        self.success = result['success']
        return result['success']

    # Take away outdated entries (In case update fails)
    def prune_price_list(self):
        # print("pruning")
        now = datetime.now()
        for price_area_name in self._price_list:
            #print(price_area_name)
            for index, entry in enumerate(self._price_list[price_area_name]):
                #print(index, entry)
                if(now - entry['time'] > timedelta(hours=1) ):
                    # print("Deleting:", index , self._price_list[price_area_name][index])
                    del self._price_list[price_area_name][index]
                pass

    def time_to_update(self):
        # print("Checking if it's time to update price list")
        now = datetime.now()
        update = 1
        while True:
            try:
                first_area = next(iter(self._price_list.items()))
                update = 2
                #print(first_area[1][0]['time'],now - first_area[1][0]['time'], timedelta(hours=1))
                if now - first_area[1][0]['time'] > timedelta(hours=1): break
                update = 3
                if now - self.update_time > timedelta(hours=1): break
                update = 4
            except Exception as e:
                update = 5
                #print(str(e))
                break
            update = False
            break
        # print("Update: ",update)
        return bool(update)

    # Get list of current and future spot price
    def prices(self, price_area=None):
        if self.time_to_update():
            self.update_price_list()

        if price_area is not None and price_area in self._price_list:
            return self._price_list[price_area]
        else:
            return self._price_list

def ascii_graph(table: dict, x_lable: bool = True, y_lable: bool = True):
    ascii_graph = ""
    data = [*table.values()]
    x_list = [time.hour() for time in table]
    if y_lable:
        ascii_graph += str(max(data)) + "\n"
    ascii_graph += textgraph.spark(data) + "\n"
    if x_lable:
        first_hour = str(x_list[0])
        last_hour = str(x_list[-1])
        if len(first_hour)+len(last_hour)+1 <= len(data):
            ascii_graph += first_hour
            ascii_graph += " "*(len(data)-len(first_hour)-len(last_hour))
        else:
            ascii_graph += " "*(len(data)-len(last_hour))
        ascii_graph += last_hour + "\n"
    return ascii_graph

# Usages
spot_price = SpotPrice()

print("Price area codes:")
print(spot_price.areas())

print("Current and future spot prices for DK2:")
table = spot_price.prices('DK2')
for entry in table:
    print(entry.hour(),table[entry])
print(ascii_graph(table))


print("All spot prices:")
table = spot_price.prices()
for area in table:
    print(area, ascii_graph(table[area]) )

#print("Spot priser DK2",spot_price.prices('DK2'))
#pprint(spot_price.prices('DK2'))
#spot_price.ascii_graph("DK2")
