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

def get_sheet(spreadsheet: gspread.spreadsheet.Spreadsheet, sheet_name: str):
    return spreadsheet.worksheet(sheet_name)

def generate_transactional_id():
    return str(uuid.uuid4())
