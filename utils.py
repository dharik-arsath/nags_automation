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


def to_dict(obj, visited=None):
    if visited is None:
        visited = set()

    obj_id = (type(obj), obj.id)  # unique identifier
    if obj_id in visited:
        return None  # avoid recursion
    visited.add(obj_id)

    result = {c.name: getattr(obj, c.name) for c in obj.__table__.columns}

    for rel in obj.__mapper__.relationships:
        value = getattr(obj, rel.key)
        if value is not None:
            if rel.uselist:
                result[rel.key] = [to_dict(i, visited) for i in value]
            else:
                result[rel.key] = to_dict(value, visited)
    return result
