from sheets.sheet_helper import get_workbook, get_sheet
from sheets.sheet_dto import ValidateExpenseInfo
from tenacity import retry,wait_exponential



COLUMN_MAPPING = {
    "ORDER ID" : "",
    "TRANSACTION ID": "",
    "PETROL": "Petrol",
    "FOOD": "Food",
    "PUNCTURE": "Puncture",
    "KEY": "Key",
    "VEHICLE_REPAIR": "Vehicle_Repair",
    "TOTAL EXPENSE": "",
}



class ExpenseSheetHandler:
    def __init__(self, gc, expense_info: ValidateExpenseInfo):        
        self.gc                  = gc
        self.workbook            = get_workbook(self.gc, "nags_automation")
        self.sheet               = get_sheet(self.workbook, "Total Expense")
        self.expense_info        = expense_info
        self._total_expense       = 0

    @property
    def total_expense(self):
        return self._total_expense

    @total_expense.setter
    def total_expense(self, val):
        self._total_expense = val 
    
    def compute_expense(self):
        headers = self.sheet.row_values(1)
        row_data = []
        for header in headers:
            if header not in COLUMN_MAPPING:
                row_data.append("")
                continue 
            
            
            key         = COLUMN_MAPPING[header]
            if self.expense_info.expenses.get(key) is not None:
                value   = self.expense_info.expenses[key]
                self.total_expense += value 
            else:
                value   = ""

            
            # if header == "TRANSACTION ID":
            #     value = self.expense_info.transaction_id
            if header == "ORDER ID":
                value = self.expense_info.transaction_id

            row_data.append(value)
        
        try:
            total_expense_idx = headers.index("TOTAL EXPENSE")
            row_data[total_expense_idx] = self.total_expense
        except Exception as e:
            print(e)
            print("Not able to find column TOTAL EXPENSE")
        
        return row_data
    
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
    def add_expense_row(self):
        row = self.compute_expense()
        return self.sheet.append_row(row)
