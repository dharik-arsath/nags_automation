import json

from db_dao import DB_DAO
from loguru import logger
from sqlalchemy.orm import Session
from utils import to_dict


class DB_Service:
    def __init__(self, session: Session):
        self.data_dao = DB_DAO(session)
        self.logger = logger

    def load_data(self):
        with open("data.json") as f:
            data = json.load(f)
        return data

    def get_raw_data(self) -> dict:
        products = self.data_dao.get_products()
        products_dict = list(map(to_dict, products))
        out = dict()

        for product in products_dict:
            out[product["name"]] = product
            out[product["name"]]["discount"] = out[product["name"]].pop("discounts")
            out[product["name"]]["commission"] = out[product["name"]].pop("commissions")
            out[product["name"]]["gain"] = out[product["name"]].pop("gains")

        return out

    def get_all_expenses(self):
        expenses = self.data_dao.get_all_expenses()
        return [expense.name for expense in expenses]

    def get_drivers(self):
        drivers = self.data_dao.get_drivers()
        return [driver.name for driver in drivers]

    def get_lines(self):
        lines = self.data_dao.get_lines()
        return [line.name for line in lines]


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    engine = create_engine("sqlite:///database.db")
    session = Session(engine)

    data_handler = DB_Service(session)
    # all_expenses = data_handler.get_all_expenses()
    products = data_handler.get_raw_data()
    products
    # product_dict = {c.name: getattr(products[0], c.name) for c in products[0].__table__.columns}

    products["Soda"]["discount"]
