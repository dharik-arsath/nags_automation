from flask import Blueprint
from db_service import DB_Service
from database import db_session

data_bp = Blueprint(__name__, "data_bp")
# handler = JsonDataHandler()


handler = DB_Service(db_session)


@data_bp.route("/get_raw_data")
def get_raw_data():
    data = handler.get_raw_data()
    print("*" * 10)
    return data


@data_bp.route("/get_all_expenses")
def get_all_expenses():
    return handler.get_all_expenses()


@data_bp.route("/get_drivers")
def get_drivers():
    return handler.get_drivers()


@data_bp.route("/get_line")
def get_line():
    return handler.get_lines()
