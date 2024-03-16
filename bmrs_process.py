import requests
from datetime import datetime, timedelta
import pandas as pd

class BMRS:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://data.elexon.co.uk/bmrs/api/v1/balancing/physical"

    def ModifyDates(self, start_date, end_date):
        # Convert the string to datetime objects
        start_datetime = datetime.fromisoformat(start_date.rstrip('Z'))
        end_datetime = datetime.fromisoformat(end_date.rstrip('Z'))

        # Check if the minutes part of the start time is divisible by 30
        if start_datetime.minute % 30 == 0:
            # Add 30 minutes to start time
            start_datetime += timedelta(minutes=30)

        # Check if the minutes part of the end time is divisible by 30
        if end_datetime.minute % 30 == 0:
            # Subtract 30 minutes from end time
            end_datetime -= timedelta(minutes=30)

        # Convert modified datetimes back to strings
        modified_start_date = start_datetime.isoformat() + 'Z'
        modified_end_date = end_datetime.isoformat() + 'Z'

        return modified_start_date, modified_end_date

    def GetPhysicalData(self, bm_unit, start_date, end_date):
        print("before",start_date)
        print("b4 type",type(start_date))
        start_date, end_date = self.ModifyDates(start_date, end_date)
        print("after",start_date)
        print("after end",end_date)
        print("after type",type(start_date))
        params = {
            "bmUnit": bm_unit,
            "from": start_date,
            "to": end_date,
            "dataset": "PN",
            "APIKey": self.api_key
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            return response.json()["data"]
        else:
            print(f"Failed to query physical data. Status code: {response.status_code}")
            return []

api_key = "l9jjurknxu8kkzv"
bm_unit = "2__HFLEX001"
start_date = "2022-09-22T20:00Z"

end_date = "2022-09-22T20:30Z"

BMRSservice = BMRS(api_key)
data = BMRSservice.GetPhysicalData(bm_unit, start_date, end_date)
df = pd.DataFrame(data)
print(df)