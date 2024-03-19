import tkinter as tk
import requests
import pandas as pd
import json

from tkinter import ttk
from tkinter import scrolledtext #For scroll bar
from tabulate import tabulate #To display the records as a table in Tkinter display

def custom_fill(group):
        print(f'group {group} type {type(group)}')
        # levelTo = group.iloc[-1]["levelTo"]
        group = group.iloc[0]
        # group['levelTo'] = levelTo
        return group


class BMRSAnalyzer(tk.Tk):
    """A GUI application for analyzing data from the BMRS API.

    This class represents a tkinter application for querying data from the BMRS API
    based on user input such as start date, end date, frequency, and BM unit.
    The queried data is displayed in a scrolled text area within the GUI.
    """

    def __init__(self, api_key):
        super().__init__()
        self.title("BMRS Analyzer")
        self.api_key = api_key
        self.api_url = "https://data.elexon.co.uk/bmrs/api/v1/balancing/physical"
        
        #Start Date
        self.start_date_label = tk.Label(self, text="Start Date:")
        self.start_date_label.pack()
        self.start_date_entry = tk.Entry(self)
        self.start_date_entry.insert(0, "2022-09-22T20:00Z") #Placeholder value
        self.start_date_entry.pack()

        # End Date
        self.end_date_label = tk.Label(self, text="End Date:")
        self.end_date_label.pack()
        self.end_date_entry = tk.Entry(self)
        self.end_date_entry.insert(0, "2022-09-22T20:30Z")  #Placeholder value
        self.end_date_entry.pack()

        # Frequency
        self.frequency_label = tk.Label(self, text="Frequency (minutes):")
        self.frequency_label.pack()
        self.frequency_entry = tk.Entry(self)
        self.frequency_entry.insert(0, "30") #Placeholder value
        self.frequency_entry.pack()

        # BM Unit
        self.bmunit_label = tk.Label(self, text="BM Unit:")
        self.bmunit_label.pack()
        self.bmunit_combo = ttk.Combobox(self)
        self.bmunit_combo.pack()
        self.bmunit_combo['values'] = self.getBmuValues()  # Provide a list of BM units
        self.bmunit_combo.set("2__HFLEX001")

        #Analyse Button
        self.analyse_button = tk.Button(self, text="Analyse", command=self.analyse)
        self.analyse_button.pack()

        # Create scrolled text area
        self.output_text = scrolledtext.ScrolledText(self, wrap='word')
        self.output_text.pack(fill=tk.BOTH, expand=True)

    #TODO: Change this to use some API instead of reading BM Units from a file    
    def getBmuValues(self):


        # Read only the "BM Unit ID" column from the CSV file and convert it to a list
        BMU_ids = pd.read_csv("./reg_bm_units.csv", usecols=["BM Unit ID"],skiprows=2).squeeze().tolist()
        return BMU_ids

    

    def DataResample(self, df, target_frequency, start_date, end_date):
        # print(f'freq {frequency} type {type(frequency)}')
        # df.set_index('timeFrom', inplace=True)
        # if int(frequency[:-1]) >= 30:
        #     ret_df = df.resample(frequency).apply(custom_fill)
            
        # else:
        #     print("myr")
        #     ret_df = df.resample(frequency).ffill()
        # print(f'B4 ret df {ret_df}')
        # ret_df.reset_index(inplace=True)
        # ret_df['timeTo'] = ret_df['timeFrom'] + pd.Timedelta(minutes=int(frequency[:-1]))
        # print(f'af ret df {ret_df}')
        # return ret_df



        # new_rows = []
        # currentTimeFrom = start_date
        # while currentTimeFrom < end_date:
        #     timeEnd = min(currentTimeFrom + pd.Timedelta(minutes=target_frequency), pd.to_datetime(end_date))
            
        #     if target_frequency > 30:
        #         relevant_rows = df[(df['timeFrom']>=currentTimeFrom) & (df['timeTo'] <= timeEnd)]
        #         if not relevant_rows.empty:
        #             new_row = relevant_rows.iloc[0].copy()
        #             new_row["timeFrom"] = currentTimeFrom
        #             new_row["timeTo"] = max(relevant_rows.iloc[-1]['timeTo'], timeEnd)
        #             new_row["levelFrom"] = relevant_rows.iloc[0]["levelFrom"]
        #             new_row["levelTo"] = relevant_rows.iloc[-1]["levelTo"]
        #             new_rows.append(new_row)
        #         currentTimeFrom = timeEnd
            
        #     else:
        #         relevant_rows = df[((df["timeFrom"] <= currentTimeFrom) & (df["timeTo"] >= timeEnd))]
        #         if not relevant_rows.empty:
        #             new_row = relevant_rows.iloc[0].copy()
        #             new_row["timeFrom"] = currentTimeFrom
        #             new_row["timeTo"] = timeEnd
        #             new_row["levelFrom"] = relevant_rows.iloc[0]["levelFrom"]
        #             new_row["levelTo"] = relevant_rows.iloc[-1]["levelTo"]
        #             new_rows.append(new_row)
        #         else:
        #             relevant_rows = df[((df["timeFrom"] <= currentTimeFrom) & (df["timeTo"] <= timeEnd))]
        #             new_row = relevant_rows.iloc[-1].copy()
        #             new_row["timeFrom"] = currentTimeFrom
        #             new_row["timeTo"] = timeEnd
        #             new_rows.append(new_row)
        #         currentTimeFrom += pd.Timedelta(minutes=target_frequency)
        
        # ret_df = pd.DataFrame(new_rows)
        # return ret_df
        new_rows = []
        currentTimeFrom = start_date
        while currentTimeFrom < end_date:
            timeEnd = min(currentTimeFrom + pd.Timedelta(minutes=target_frequency), end_date)
            
            # Select relevant rows within the current time window
            relevant_rows = df[(df['timeFrom'] < timeEnd) & (df['timeTo'] >= currentTimeFrom)]
            
            if not relevant_rows.empty:
                # Create a new row based on the first and last relevant rows
                new_row = {
                    "settlementDate": relevant_rows.iloc[0]["settlementDate"],
                    "settlementPeriod": relevant_rows.iloc[0]["settlementPeriod"],
                    "timeFrom": currentTimeFrom,
                    "timeTo": timeEnd,
                    "levelFrom": relevant_rows.iloc[0]["levelFrom"],
                    "levelTo": relevant_rows.iloc[-1]["levelTo"]
                }
                new_rows.append(new_row)
            
            currentTimeFrom = timeEnd

        ret_df = pd.DataFrame(new_rows)
        return ret_df
                    



    def invokeAPI(self, params):
        """
        Invoke the BMRS API and retrieve data.

        This method makes a HTTP GET request to the BMRS API with the provided params.
        If the request is successful, it retrieves the data from the response,
        converts it to a pandas DataFrame, and formats it as a tabulated string using the tabulate library.
        If the request fails, it prints an error message and returns a dict with error message.

        Args:
            params (dict): A dictionary containing the parameters to be passed to the API.

        Returns:
            str: A tabulated string representation of the data if the API call is successful,
                otherwise a dict with error message.
        """
        response = requests.get(self.api_url, params=params)
        if response.status_code == 200:
            data = response.json()["data"]
            df = pd.DataFrame(data)
            if df.shape[0]==0:
                df_str = "No records found...Try changing the parameters"
            else:
                print(f'ivde shape {df.shape}')
                df['timeFrom'] = pd.to_datetime(df['timeFrom'])
                df['timeTo'] = pd.to_datetime(df['timeTo'])
                filtered_df = df[(df['timeFrom'] >= pd.to_datetime(params["from"])) & (df['timeTo'] <= pd.to_datetime(params["to"]))]

                filtered_df = filtered_df.sort_values(by='timeFrom', ascending=True).reset_index(drop=True)
                print("fdf:",filtered_df)
                print(f'filtered df shape {filtered_df.shape}')
                # self, df, frequency, start_date, end_date):
                processed_df = self.DataResample(filtered_df, params["frequency"], pd.to_datetime(params["from"]), pd.to_datetime(params["to"]))
                print(f'The returned df has shape',df.shape)
                df_str = tabulate(processed_df, headers='keys', tablefmt='grid')
            
        else:
            print(f"Failed to query physical data. Status code: {response.status_code}")
            response_json  = response.json()
            df_str = response_json.get('errors', {})
        
        return df_str

    def analyse(self):
        """Analyse the BMRS data based on user input.

        This method retrieves user input for start date, end date, frequency, and BM unit.
        It constructs the parameters required for querying the BMRS API.
        It then invokes the invokeAPI method to make the API call and retrieve the data.
        The retrieved data is displayed in the output_text area of the GUI.

        """
        # Get input values
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        frequency = int(self.frequency_entry.get())
        bm_unit = self.bmunit_combo.get()
        
        params = {
            "bmUnit": bm_unit,
            "from": start_date,
            "to": end_date,
            "dataset": "PN",
            "APIKey": self.api_key,
            "frequency":frequency
        }
        df_str = self.invokeAPI(params)
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, df_str)
        lines = len(df_str.split("\n"))
        width = max(len(line) for line in df_str.split("\n"))
        self.output_text.config(width=width, height=lines,  wrap='word')


if __name__ == "__main__":
    api_key = "l9jjurknxu8kkzv" #TODO This can be moved out by using env variables
    app = BMRSAnalyzer(api_key)
    app.mainloop()