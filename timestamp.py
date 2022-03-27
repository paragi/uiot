# Timestamp class
#
# By Simon Rigét @ paragi . dk 2022 License MIT
#
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

class Timestamp:
    def __init__(self, value = 0, format = ""):
        self.timestamp: float = 0
        if isinstance(value, int) or isinstance(value, float):
            self.timestamp = float(value)
        elif isinstance(value, datetime):
            self.timestamp = float(time.mktime(value.timetuple()))
        elif isinstance(value, str):
            if format == "": format = '%Y-%m-%dT%H:%M:%S%z' #ISO format
            self.timestamp = float(time.mktime(datetime.strptime(value,format).replace(tzinfo=ZoneInfo('UTC')).timetuple()))

    def __repr__(self):
        return str(datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')))
    def __hash__(self):
        return int(self.timestamp)
    def __str__(self):
        return str(datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')))
    def __int__(self):
        return int(self.timestamp)
    def __float__(self):
        return float(self.timestamp)

    def second(self):
        return datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')).second
    def minute(self):
        return datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')).minute
    def hour(self):
        return datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')).hour
    def day(self):
        return datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')).day
    def month(self):
        return datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')).month
    def year(self):
        return datetime.fromtimestamp(self.timestamp).astimezone(ZoneInfo('localtime')).year

    def __lt__(self, other):
        return self.timestamp < other.timestamp
    def __le__(self, other):
        return self.timestamp <= other.timestamp
    def __gt__(self, other):
        return self.timestamp > other.timestamp
    def __ge__(self, other):
        return self.timestamp >= other.timestamp
    def __eq__(self, other):
        return self.timestamp == other.timestamp


'''
print("Test with ",datetime.now())
ts = Timestamp(datetime.now())
print("Ts",ts)
print("Float",float(ts))
print("str",str(ts))
print("second",ts.second())
print("minute",ts.minute())
print("hour",ts.hour())
print("day",ts.day())
print("month",ts.month())
print("year",ts.year())
'''