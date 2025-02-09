from pydantic import BaseModel, Field
from typing import List, Sequence, Optional
import gspread


class SheetManager(BaseModel):
    gc: gspread.client.Client
    spreadsheet: gspread.spreadsheet.Spreadsheet
    worksheet  : gspread.worksheet.Worksheet

    class Config:
        arbitrary_types_allowed=True

class SheetInfo(BaseModel):
    date                            : str
    time                            : str 
    driver_name                     : str
    line                            : str
    product_name                    : str 
    base_amount                     : float
    final_amount                    : float
    discount                        : List[ dict[str, int | float] ]
    commission                      : List[ dict[str, int | float] ]
    goods_upload_cases              : int 
    goods_upload_pieces             : int 
    goods_return_cases              : int 
    goods_return_pieces             : int 
    cases                           : int 
    pieces                          : int 
    kuraivu_cases                   : int
    kuraivu_pieces                  : int
    kuraivu_amount                  : float
    adhiga_varavu_cases             : int
    adhiga_varavu_pieces            : int


class ValidateSheetInfo(BaseModel):
    transaction_id  : int
    total_expense   : float 
    credits         : dict[str, int | float]

    entries         : Sequence[SheetInfo]

class ValidateExpenseInfo(BaseModel):
    transaction_id  : int
    expenses        : Optional[dict[str, float]] = Field(default=None)