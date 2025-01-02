import uuid


def parse_expense(prod: dict):
    expense_parser = dict()
    if len( prod["expenses"] ) == 0:
        return 
    
    for expense in prod["expenses"]:
        expense_parser[ expense["description"] ] = expense["amount"]

    return expense_parser


# Define a function to generate a unique ID
def generate_id():
    return str(uuid.uuid4())