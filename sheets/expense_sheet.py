from sheets.sheet_helper import get_workbook, get_sheet
from sheets.sheet_dto import ValidateExpenseInfo
from tenacity import retry,wait_exponential
from copy import deepcopy


COLUMN_MAPPING = {
    "ORDER ID" : "",
    "TRANSACTION ID": "",
    "PETROL": "Petrol",
    "FOOD": "Food",
    "PUNCTURE": "Puncture",
    "KEY": "Key",
    "VEHICLE_REPAIR": "Vehicle_Repair",
    "OTHER" : "",
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
        expenses = deepcopy(self.expense_info.expenses)

        headers = self.sheet.row_values(1)
        row_data = []
        for header in headers:
            if header not in COLUMN_MAPPING:
                row_data.append("")
                continue 
            

            key         = COLUMN_MAPPING[header]
            if expenses.get(key) is not None:
                value   = expenses.pop( key )
                self.total_expense += value 
            else:
                value   = ""

            if header == "ORDER ID":
                value = self.expense_info.transaction_id

            row_data.append(value)
        
        if len(expenses) > 0:
            other_expenses = dict()
        
            for k,v in expenses.items():
                self.total_expense += v 
                if other_expenses.get(k) is None:
                    other_expenses[k] = v 
                else:
                    other_expenses[k] += v 
        
            other_idx = headers.index("OTHER")
            row_data[other_idx] = str(other_expenses)

        try:
            total_expense_idx = headers.index("TOTAL EXPENSE")
            row_data[total_expense_idx] = self.total_expense
        except Exception as e:
            print(e)
            print("Not able to find column TOTAL EXPENSE")
        
        return row_data
    
    @retry(wait=wait_exponential(multiplier=1, min=4, max=10), reraise=True)
    def add_expense_row(self, row: list):
        return self.sheet.append_row(row)