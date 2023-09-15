import pandas as pd
import json
from datetime import datetime
from time import sleep


def workbook_name():
    now = datetime.now().strftime("%Hhr%Mmin")
    date = datetime.now().strftime("%Y-%m-%d")
    return f"[Export] XLSX/[Rentals] {now} {date}.xlsx"


def save_to_json(workbook_name_static):
    print("Saving to JSON...")
    sleep(3)
    # Read the Excel file
    dataframe = pd.read_excel(workbook_name_static)

    # Convert to JSON
    json_data = dataframe.to_json()
    json_data = json.loads(json_data)

    f = open("[Export] JSON/" + workbook_name_static[14:-5] + ".json", "w")  # Open the file to write the logs
    f.write(json.dumps(json_data, sort_keys=True, indent=2))  # Write the list_user to the
    # log_user.txt file
    f.close()  # Close the file
