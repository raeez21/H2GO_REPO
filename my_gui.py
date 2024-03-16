import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext 
import requests
import pandas as pd
import json
from tabulate import tabulate

class BMRSAnalyzer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMRS Analyzer")
        self.start_date_label = tk.Label(self, text="Start Date:")
        self.start_date_label.pack()
        self.start_date_entry = tk.Entry(self)
        self.start_date_entry.insert(0, "2022-09-22T20:00Z")
        self.start_date_entry.pack()

        # End Date
        self.end_date_label = tk.Label(self, text="End Date:")
        self.end_date_label.pack()
        self.end_date_entry = tk.Entry(self)
        self.end_date_entry.insert(0, "2022-09-22T20:30Z") 
        self.end_date_entry.pack()

        # Frequency
        self.frequency_label = tk.Label(self, text="Frequency (minutes):")
        self.frequency_label.pack()
        self.frequency_entry = tk.Entry(self)
        self.frequency_entry.insert(0, "30")
        self.frequency_entry.pack()

        # BM Unit
        self.bmunit_label = tk.Label(self, text="BM Unit:")
        self.bmunit_label.pack()
        self.bmunit_entry = tk.Entry(self)
        self.bmunit_entry.insert(0, "2__HFLEX001")
        self.bmunit_entry.pack()

        self.analyse_button = tk.Button(self, text="Analyse", command=self.analyse)
        self.analyse_button.pack()

        # Create scrolled text area
        self.output_text = scrolledtext.ScrolledText(self, wrap='word')
        self.output_text.pack(fill=tk.BOTH, expand=True)
        # self.root = root
        # self.root.title("BMRS Analyzer")

        # # Create labels and entry fields
        # self.start_date_label = ttk.Label(root, text="Start Date:")
        # self.start_date_entry = ttk.Entry(root)
        # self.start_date_entry.insert(0, "2022-09-22T20:00Z")  # Example placeholder

        # self.end_date_label = ttk.Label(root, text="End Date:")
        # self.end_date_entry = ttk.Entry(root)
        # self.end_date_entry.insert(0, "2022-09-22T20:30Z")  # Example placeholder

        # self.frequency_label = ttk.Label(root, text="Frequency (minutes):")
        # self.frequency_entry = ttk.Entry(root)
        # self.frequency_entry.insert(0, "30")  # Example default value

        # self.bmunit_label = ttk.Label(root, text="BMUnit:")
        # self.bmunit_entry = ttk.Entry(root)
        # self.bmunit_entry.insert(0, "2__HFLEX001")  # Example default value

        # # Create Analyse button
        # self.analyse_button = ttk.Button(root, text="Analyse", command=self.analyse)

        # # Create text area to display data
        # # self.output_text = tk.Text(root, height=20, width=50)
        # self.output_text = scrolledtext.ScrolledText(root, wrap='word')
        # self.output_text.pack(fill=tk.BOTH, expand=True)

        # # Grid layout
        # self.start_date_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        # self.start_date_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        # self.end_date_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        # self.end_date_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        # self.frequency_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        # self.frequency_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        # self.bmunit_label.grid(row=3, column=0, padx=5, pady=5, sticky="w")
        # self.bmunit_entry.grid(row=3, column=1, padx=5, pady=5, sticky="w")
        # self.analyse_button.grid(row=4, columnspan=2, padx=5, pady=5)
        # self.output_text.grid(row=5, columnspan=2, padx=5, pady=5)

    def analyse(self):
        # Get input values
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()
        frequency = self.frequency_entry.get()
        bmunit = self.bmunit_entry.get()

        # Make API call
        url = f"https://data.elexon.co.uk/bmrs/api/v1/balancing/physical?bmUnit={bmunit}&from={start_date}&to={end_date}&dataset=PN"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()["data"]
            df = pd.DataFrame(data)
            print(df)
            # df_str = df.to_string(index=False)
            df_str = tabulate(df, headers='keys', tablefmt='grid')
        else:
            print(f"Failed to query physical data. Status code: {response.status_code}")
            response_json  = response.json()
            df_str = response_json.get('errors', {})
            print(f"Respone tex {df_str} tpe {type(df_str)}")
        # Display response in the text area
        self.output_text.delete("1.0", tk.END)
        self.output_text.insert(tk.END, df_str)
        lines = len(df_str.split("\n"))
        width = max(len(line) for line in df_str.split("\n"))
        self.output_text.config(width=width, height=lines,  wrap='word')


if __name__ == "__main__":
    # root = tk.Tk()
    app = BMRSAnalyzer()
    app.mainloop()