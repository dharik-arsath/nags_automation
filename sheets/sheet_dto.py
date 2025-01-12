from pydantic import BaseModel, Field
from typing import Sequence, Optional

class SheetInfo(BaseModel):
    date                            : str
    time                            : str 
    driver_name                     : str
    line                            : str
    product_name                    : str 
    base_amount                     : float
    final_amount                    : float
    discount                        : float
    commission                      : float
    kuraivu_cases                   : int
    kuraivu_pieces                  : int
    kuraivu_amount                  : float
    adhiga_varavu_cases             : int
    adhiga_varavu_pieces            : int 


class ValidateSheetInfo(BaseModel):
    transaction_id  : int
    total_expense   : float 

    entries         : Sequence[SheetInfo]

class ValidateExpenseInfo(BaseModel):
    transaction_id  : int
    expenses        : Optional[dict[str, float]] = Field(default=None)