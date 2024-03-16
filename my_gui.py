import tkinter as tk
import requests
import pandas as pd
import json

from tkinter import ttk
from tkinter import scrolledtext #For scroll bar
from tabulate import tabulate #To display the records as a table in Tkinter display


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
        
    def getBmuValues(self):
        # Read only the "BM Unit ID" column from the CSV file and convert it to a list
        BMU_ids = pd.read_csv("./reg_bm_units.csv", usecols=["BM Unit ID"],skiprows=2).squeeze().tolist()
        return BMU_ids
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
            print(f'The returned df has shape',df.shape)
            df_str = tabulate(df, headers='keys', tablefmt='grid')
            if df.shape[0]==0:
                df_str = "No records found...Try changing the parameters"
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
        frequency = self.frequency_entry.get()
        bm_unit = self.bmunit_combo.get()
        
        params = {
            "bmUnit": bm_unit,
            "from": start_date,
            "to": end_date,
            "dataset": "PN",
            "APIKey": self.api_key
        }
        df_str = self.invokeAPI(params)
        
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, df_str)
        lines = len(df_str.split("\n"))
        width = max(len(line) for line in df_str.split("\n"))
        self.output_text.config(width=width, height=lines,  wrap='word')


if __name__ == "__main__":
    api_key = "l9jjurknxu8kkzv"
    app = BMRSAnalyzer(api_key)
    app.mainloop()