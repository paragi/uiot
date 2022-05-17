
# Energinet data service API

import json
import urllib.request
from datetime import *

from machine import Pin, SoftI2C
import ssd1306

'''
{"query":"query Dataset {elEnergiDataservices( order_by: {HourUTC: desc} limit: 100 offset: 0){HourUTC HourDK PriceArea EnergiDataserviceDKK EnergiDataserviceEUR }}"}

Search a DataStore resource.

    The datastore_search action allows you to search data in a resource.
    DataStore resources that belong to private CKAN resource can only be
    read by you if you have access to the CKAN resource and send the
    appropriate authorization.

    :param resource_id: id or alias of the resource to be searched against
        :type resource_id: string
    :param filters: matching conditions to select, e.g
                    {"key1": "a", "key2": "b"} (optional)
        :type filters: dictionary
    :param q: full text query. If it's a string, it'll search on all fields on
              each row. If it's a dictionary as {"key1": "a", "key2": "b"},
              it'll search on each specific field (optional)
        :type q: string or dictionary
    :param distinct: return only distinct rows (optional, default: false)
        :type distinct: bool
    :param plain: treat as plain text query (optional, default: true)
        :type plain: bool
    :param language: language of the full text query
                     (optional, default: english)
        :type language: string
    :param limit: maximum number of rows to return (optional, default: 100)
        :type limit: int
    :param offset: offset this number of rows (optional)
        :type offset: int
    :param fields: fields to return
                   (optional, default: all fields in original order)
        :type fields: list or comma separated string
    :param sort: comma separated field names with ordering
                 e.g.: "fieldname1, fieldname2 desc"
      :type sort: string
    :param include_total: True to return total matching record count
                          (optional, default: true)
        :type include_total: bool
    :param records_format: the format for the records return value:
        'objects' (default) list of {fieldname1: value1, ...} dicts,
        'lists' list of [value1, value2, ...] lists,
        'csv' string containing comma-separated values with no header,
        'tsv' string containing tab-separated values with no header
     :type records_format: controlled list


    Setting the ``plain`` flag to false enables the entire PostgreSQL
    `full text search query language`_.

    A listing of all available resources can be found at the
    alias ``_table_metadata``.

    .. _full text search query language: http://www.postgresql.org/docs/9.1/static/datatype-textsearch.html#DATATYPE-TSQUERY

    If you need to download the full resource, read :ref:`dump`.

    **Results:**

    The result of this action is a dictionary with the following keys:

    :rtype: A dictionary with the following keys
    :param fields: fields/columns and their extra metadata
    :type fields: list of dictionaries
    :param offset: query offset value
    :type offset: int
    :param limit: query limit value
    :type limit: int
    :param filters: query filters
    :type filters: list of dictionaries
    :param total: number of total matching records
    :type total: int
    :param records: list of matching results
    :type records: depends on records_format value passed

    url = 'https://api.energidataservice.dk/datastore_search?resource_id=elEnergiDataservices'
    url = 'https://api.energidataservice.dk/datastore_search?resource_id=elEnergiDataservices&filters={PriceArea: {_eq: \"DK2\"}}'
'''


# Retrieve dataset from SQL query with energi data service
# See https://www.energidataservice.dk for details
# Issues with:
#   price in DKK missing at times
#   HourDK summertime not always corrected.
#   SQL capabilities very limited
# Use UTC and price in EUR
class EnergiDataservice:
    def __init__(self):
        self._price_list = {}
        self.update_time = 0.0
        self.success = False

    def Retrieve_sql_dataset_from_server(self, query: object) -> object:
        uri = "https://api.energidataservice.dk/datastore_search_sql?sql="
        print("Get:", uri + query)
        print(uri + urllib.parse.quote(query.strip()))
        fileobj: object = urllib.request.urlopen(uri + urllib.parse.quote(query.strip()))
        result_dict = json.loads(fileobj.read())
        return result_dict

    # Get list of Price Area names
    def price_area_name_list(self):
        query = '''
            SELECT DISTINCT "PriceArea" 
            FROM "elEnergiDataservices"
            ORDER BY "PriceArea"
            '''
        result = self.Retrieve_sql_dataset_from_server(query)
        return [li["PriceArea"] for li in [*result["result"]["records"]]]

    # Get current spot price list, from now
    # Creates a list of price price_area_name_list, containing lists of time tags and spot price
    def update_price_list(self):
        query = '''
                        SELECT "PriceArea", "HourUTC", "EnergiDataserviceEUR"
                        FROM "elEnergiDataservices"
                        WHERE "HourUTC" >= NOW()
                        ORDER BY "PriceArea", "HourUTC"
                        '''
        result = self.Retrieve_sql_dataset_from_server(query)
        # pprint(result)
        print("Updating price list")
        if result['success']:
            self._price_list = {}

            for entry in result["result"]["records"]:
                try:
                    if not entry["PriceArea"] in self._price_list:
                        self._price_list[entry["PriceArea"]] = {}
                    # print(entry)

                    timestamp = datetime.strptime(entry["HourUTC"], '%Y-%m-%dT%H:%M:%S%z').timestamp()
                    price = round(float(entry["EnergiDataserviceEUR"]) / 1000, 3)
                    self._price_list[entry["PriceArea"]][timestamp] = price
                    # print(entry,timestamp, price)
                    self.update_time = int(datetime.now().timestamp())
                except Exception as e:
                    pass

        self.prune_price_list()
        # print(self._price_list)
        self.success = result['success']
        return result['success']

    # Take away outdated entries (In case update fails)
    def prune_price_list(self):
        print("pruning")
        now = datetime.now().timestamp()
        for price_area_name in self._price_list:
            #print(price_area_name)
            for index in self._price_list[price_area_name]:
                #print(index, now - int(index))
                if now - int(index) > 3600 :
                    print("Deleting:", index , self._price_list[price_area_name][index])
                    del self._price_list[price_area_name][index]
                else:
                    break

    def time_to_update(self):
        # print("Checking if it's time to update price list")
        now = datetime.now().timestamp()
        update = 1
        while True:
            try:
                if len(self._price_list) < 1: break
                first_time_index = int(next(iter(self._price_list[next(iter(self._price_list))])))
                # print("first a:",first_time_index, now - int(self.update_time) )
                update = 2
                if now - first_time_index > 3600: break
                update = 3
                if (now - int(self.update_time)) > 3600: break
                update = 4
                if not self.success and now - int(self.update_time) > 60: break
            except Exception as e:
                update = 5
                print(update,repr(e))
                break
            update = False
            break

        # print("Update: ",update)
        return bool(update)

    # Get list of current and future spot price
    def spot_price_table(self, price_area=None):
        if self.time_to_update():
            self.update_price_list()

        if price_area is not None and price_area in self._price_list:
            return self._price_list[price_area]
        else:
            return self._price_list


def ascii_graph(table: dict, x_lable: bool = True, y_lable: bool = True):
    ascii_graph = ""
    data = [*table.values()]
    x_list = [datetime.fromtimestamp(time).hour for time in table]
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


if __name__ == "__main__":
    spot_price = EnergiDataservice()

    print("Price area codes:")
    print(spot_price.price_area_name_list())

    print("Current and future spot spot_price_table for DK2:")
    table = spot_price.spot_price_table('DK2')

    for entry in table:
        print(datetime.fromtimestamp(entry).hour,table[entry])
    print(ascii_graph(table))

    print("All spot spot_price_table:")
    table = spot_price.spot_price_table()
    for area in table:
        print(area, ascii_graph(table[area]) )

    print("Limit to 24 hours of DK2:")
    table = spot_price.spot_price_table('DK2')
    print(ascii_graph(dict(list(table.items())[:24])))



    # ESP32 Pin assignment
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

    # ESP8266 Pin assignment
    # i2c = SoftI2C(scl=Pin(5), sda=Pin(4))

    oled_width = 128
    oled_height = 64
    oled = ssd1306.SSD1306_I2C(oled_width, oled_height, i2c)

    oled.text('Hello, World 1!', 0, 0)
    oled.text('Hello, World 2!', 0, 10)
    oled.text('Hello, World 3!', 0, 20)

    oled.show()