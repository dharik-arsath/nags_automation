import gspread
from utils import parse_expense


#dep id = AKfycbxEoJW56-68jritKZlByqAviO3AZabfNdgHBVoJeqEQaO9wB0k2evGMuknKcv3uGYuILw
#dep_url = "https://script.google.com/macros/library/d/1jydTewssnkA80NbWCeiHXF_3nZDaZVNu1glMAGAK-wADS2A-DDWQqWi4/1"

#dep_id = "AKfycbzY3wk18Epc-rsinYjrNCRlnmUof0mmltKYRG1OK_8dQoPqDq0ULbK7zOHxf8BQZj6maw"
#dep_url = "https://script.google.com/macros/s/AKfycbzY3wk18Epc-rsinYjrNCRlnmUof0mmltKYRG1OK_8dQoPqDq0ULbK7zOHxf8BQZj6maw/exec"

gc = gspread.service_account("credentials.json")
spreadsheet = gc.open("nags_automation")
report_sheet = spreadsheet.worksheet("Sheet2")


def get_avg_expense(data_dict, total_products):
    total_expense = 0
    expenses: list[dict] = data_dict["expenses"]
    total_count_products = total_products
    for expense in expenses:
        for k,v in expense.items():
            if k == "amount":
                total_expense += v 
        
    return (total_expense / total_count_products)


def update_google_sheet(data_dict: dict, total_products:int):
    """
    Update Google Sheet using column mapping for resilient data insertion
    
    Args:
        data_dict (dict): Dictionary containing data to be inserted
            Keys should match the column headers in the Google Sheet
    """
    # Initialize Google Sheets connection
    # gc = gspread.service_account("credentials.json")
    # spreadsheet = gc.open("nags_automation")
    # report_sheet = spreadsheet.worksheet("Sheet2")
    
    # Define column headers and their corresponding keys in your data
    COLUMN_MAPPING = {
        "TRANSACTION ID" : "",
        'DATE': 'date',
        'DRIVER NAME': 'driver_name',
        'LINE': 'line',
        'PRODUCT_NAME': "product_name",
        'BASE_AMOUNT': 'base_amount',
        'FINAL_AMOUNT': 'final_amount',
        'DISCOUNT': 'discount',
        'COMMISSION': 'commission',
        'KURAIVU_CASES': 'kuraivu_cases',
        'KURAIVU_PIECES': 'kuraivu_pieces',
        "KURAIVU_AMOUNT" : "kSheet2uraivu_amount",
        "ADHIGA_VARAVU_CASES" : "adhiga_varavu_cases" ,
        "ADHIGA_VARAVU_PIECES": "adhiga_varavu_pieces",
        # "EXPENSES" : "expenses",
        "PETROL" : "",
        "FOOD": "",
        "PUNCTURE":"",
        "KEY" : "",
        "VEHICLE_REPAIR" : "",
        "TIME" : "time",
    }
    
    # Get all column headers from the sheet
    headers = report_sheet.row_values(1)
    print(headers)
    
    # Create a list of values in the same order as the sheet headers
    row_data = []
    expenses = None
    for header in headers:
        if header in COLUMN_MAPPING:
            key = COLUMN_MAPPING[header]
            value = data_dict.get(key, '')  # Use empty string if key doesn't exist
            if header == "TRANSACTION ID":
                value = data_dict["_id"]
            
            # if header == "TOTAL_EXPENSE":
            #     value = get_avg_expense(data_dict, total_products)
            
            # if header == "FINAL_AMOUNT":
            #     avg_expense = get_avg_expense(data_dict, total_products)
            #     value -= avg_expense

            if header == "PETROL" or header == "FOOD" or header == "PUNCTURE" or header == "KEY" or header == "VEHICLE_REPAIR":
                if expenses is None:
                    expenses = parse_expense(data_dict)
                    if expenses is None:
                        value = ""
                    else:
                        value = expenses.get(header.title())
                else:
                    value = expenses.get(header.title(), 0)
            
            row_data.append(value)
        else:
            # If header doesn't exist in mapping, add empty string
            if header == "TOTAL_EXPENSE":
                continue
            
            row_data.append('')
    

    # total_expense = 0

    # expenses: list[dict] = data_dict["expenses"]
    # for expense in expenses:
    #     print(expense)
    #     for k,v in expense.items():
    #         if k == "amount":
    #             total_expense += v
        
    # row_data.append(total_expense)


    # Append the row to the sheet
    report_sheet.append_row(row_data)
    # data_dict["total_expense"] = get_avg_expense(data_dict,total_products)
    return data_dict



# gc = gspread.service_account("credentials.json")

# spreadsheet=  gc.open("nags_automation")
# report_sheet = spreadsheet.worksheet("Sheet2")

# Example usage:
# sample_data = {
#     'date': "12/1/2024",
#     'driver_name': 'Nagaraj',
#     'line': 'Sellur',
#     'base_amount': 20,
#     'final_amount': 300,
#     'discount': 10,
#     'commission': 5,
#     'kuraivu': 1,
# }

# Update the sheet
# update_google_sheet(sample_data)