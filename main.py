import json
import urllib.request
import requests


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

charge_owners()
