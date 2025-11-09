import gspread
import pandas as pd

gc = gspread.service_account("credentials.json")
spreadsheet = gc.open("nags_automation")
report_sheet = spreadsheet.worksheet("Sheet3")

# COLUMN_MAPPING = {
#     "TRANSACTION ID": "",
#     "Total Discount" : "",
#     "Total Commission": "",
#     "Total Expense" : ""
# }

# headers = report_sheet.row_values(1)
# print(headers)
# data = {"entries":[{"driver_name":"pandi","date":"2025-01-11","time":"21:01","product_name":"200ml panneer (168)","line":"athikulam","cases":10,"pieces":4,"discount":0,"commission":71.166668,"kuraivu_cases":0,"kuraivu_pieces":0,"kuraivu_amount":0,"adhiga_varavu_cases":0,"adhiga_varavu_pieces":0,"base_amount":1708,"final_amount":1636.83,"expenses":[{"description":"Vehicle_Repair","amount":600}]},{"driver_name":"pandi","date":"2025-01-11","time":"21:01","product_name":"200ml grape (168)","line":"athikulam","cases":0,"pieces":12,"discount":0,"commission":3.500004,"kuraivu_cases":0,"kuraivu_pieces":0,"kuraivu_amount":0,"adhiga_varavu_cases":0,"adhiga_varavu_pieces":0,"base_amount":84,"final_amount":80.5,"expenses":[{"description":"Vehicle_Repair","amount":600}]},{"driver_name":"pandi","date":"2025-01-11","time":"21:01","product_name":"badam milk 456","line":"athikulam","cases":0,"pieces":3,"discount":0,"commission":2.25,"kuraivu_cases":0,"kuraivu_pieces":0,"kuraivu_amount":0,"adhiga_varavu_cases":0,"adhiga_varavu_pieces":0,"base_amount":57,"final_amount":54.75,"expenses":[{"description":"Vehicle_Repair","amount":600}]},{"driver_name":"pandi","date":"2025-01-11","time":"21:01","product_name":"pet bottle orange (225)","line":"athikulam","cases":1,"pieces":0,"discount":0,"commission":7,"kuraivu_cases":0,"kuraivu_pieces":0,"kuraivu_amount":0,"adhiga_varavu_cases":0,"adhiga_varavu_pieces":0,"base_amount":225,"final_amount":218,"expenses":[{"description":"Vehicle_Repair","amount":600}]}]}


records = report_sheet.get_all_records()
df = pd.DataFrame(records)


df.groupby("TRANSACTION ID").FINAL_AMOUNT.agg(["sum"])


# # Create a list of values in the same order as the sheet headers
# row_data = []
# expenses = None
# for header in headers:
#     if header in COLUMN_MAPPING:
#         key = COLUMN_MAPPING[header]
#         value = data_dict.get(key, '')  # Use empty string if key doesn't exist
