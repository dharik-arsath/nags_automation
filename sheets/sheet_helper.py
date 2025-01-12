from pydantic import BaseModel, field_validator, ValidationInfo,  Field
from typing import Optional
import os 
import gspread
import uuid 



class AuthGsheet(BaseModel):
    credentials             : str = Field(default="credentials.json")

    @field_validator("credentials")
    def validate_crendetials(cls, v: str, info: ValidationInfo):
        if os.path.exists(v) is False:
            raise FileNotFoundError(f"File {v} does not exist...")


def authenticate(path_to_credentials: Optional[str] = None ):
    if path_to_credentials is None:
        auth_info = AuthGsheet()
    else:
        auth_info = AuthGsheet(path_to_credentials)

    gc = gspread.service_account(auth_info.credentials)
    return gc 



def get_workbook(gc: gspread.client.Client, workbook_name: str):
    return gc.open(workbook_name)

def get_sheet(spreadsheet: gspread.worksheet.Worksheet, sheet_name: str):
    return spreadsheet.worksheet(sheet_name)

def generate_transactional_id():
    return str(uuid.uuid4())


def generate_numeric_id(sheet: gspread.worksheet.Worksheet, column=1):
    """
    Generate a unique numeric ID by finding the highest ID in the specified column 
    and incrementing it.

    Args:
        sheet (gspread.Worksheet): The gspread worksheet object.
        column (int): The column number where IDs are stored (1-based index).
    
    Returns:
        int: The next numeric ID in increasing order.
    """
    # Fetch all values in the specified column
    column_values = sheet.col_values(column)
    
    # Filter out non-numeric or empty values
    numeric_ids = [int(value) for value in column_values if value.isdigit()]
    
    # Find the maximum ID and increment it
    if numeric_ids:
        next_id = max(numeric_ids) + 1
    else:
        next_id = 1  # Start with 1 if no IDs exist
    
    return next_id


def get_numeric_id_from_main_sheet(gc, sheet_name: str = "items", workbook_name: str = "nags_automation"):
    workbook = get_workbook(gc, workbook_name)
    sheet    = get_sheet(workbook, sheet_name)
    return generate_numeric_id(sheet)