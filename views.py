from flask import Flask, Request, request, jsonify, make_response
from flask import render_template
from sheet import update_google_sheet
from pydantic import BaseModel, Field
from datetime import datetime
from flask_cors import CORS
from flask import abort
import json
from notify_telegram import send_photo, send_message
import asyncio
from loguru import logger
from utils import parse_expense, generate_id
from pathlib import Path

import matplotlib.pyplot as plt
from tabulate import tabulate
from uuid import uuid4
from tabulate import tabulate


from tabulate import tabulate


# def format_msg(data):
#     # Initialize variables
#     total_amount = 0
#     discount = 0
#     commission = 0
#     expenses = {}

#     # Create table rows
#     table_rows = []
#     for item in data:
#         product_name = f"{item['product_name']}"
#         table_rows.append(["ADD", product_name, item["final_amount"]])
#         total_amount += item["final_amount"]
#         discount += item["discount"]
#         commission += item["commission"]

#     # Process expenses
#     for expense in item["expenses"]:
#         description = expense["description"]
#         amount = expense["amount"]
#         if description in expenses:
#             expenses[description] += amount
#         else:
#             expenses[description] = amount

#     # Create summary rows
#     summary_rows = [
#         ["", "Total", total_amount],
#         ["SUB", "DISCOUNT", discount],
#         ["", "TOTAL", total_amount - discount],
#         ["SUB", "COMMISSION", commission],
#         ["", "TOTAL", round(total_amount - discount - commission, 4)],
#     ]

#     # Create expense rows
#     expense_rows = []
#     total_expenses = 0
#     for description, amount in expenses.items():
#         expense_rows.append(["SUB", description, amount])
#         total_expenses += amount
#     expense_rows.append(["", "TOTAL EXPENSES", total_expenses])

#     # Create final total row
#     final_total = round(total_amount - discount - commission - total_expenses, 4)
#     final_total_row = ["", "FINAL TOTAL", final_total]

#     # Generate table
#     table = tabulate(
#         table_rows + summary_rows + expense_rows + [final_total_row],
#         headers=["", "Product", "Amount"],
#         tablefmt="grid",
#         maxcolwidths=[None, 10, None],
#     )
#     telegram_message = f"<pre>{table}</pre>"

#     return telegram_message




from tabulate import tabulate
from datetime import datetime

def format_msg(data):
    # Initialize variables
    total_amount = 0
    discount = 0
    commission = 0
    final_amount = 0
    expenses = {}

    # Get driver name, line, and date
    driver_name = data[0]['driver_name']
    line = data[0]['line']
    date = data[0]['date']

    # Create table rows
    table_rows = []
    for item in data:
        product_name = f"{item['product_name']}"
        table_rows.append(["ADD", product_name, item["base_amount"]])
        print("*" * 20)
        print(f'{item.get("adhiga_varavu_pieces")}')
        # if item.get("adhiga_varavu_pieces") is not None and item.get("adhiga_varavu_pieces") > 0:
        #     table_rows.append(["ADD", "adhuga_varavu", item["adhiga_varavu_pieces"]])
        total_amount += item["base_amount"]
        discount += item["discount"]
        commission += item["commission"]
        final_amount += item["final_amount"]

    # Process expenses
    for item in data:
        for expense in item["expenses"]:
            description = expense["description"]
            amount = expense["amount"]
            if description in expenses:
                expenses[description] += amount
            else:
                expenses[description] = amount

    # Create summary rows
    summary_rows = [
        ["", "Total", total_amount],
        ["SUB", "DISCOUNT", discount],
        ["SUB", "COMMISSION", commission],
        ["", "TOTAL", round(final_amount, 4)],
    ]

    # Create expense rows
    expense_rows = []
    total_expenses = 0
    for description, amount in expenses.items():
        expense_rows.append(["SUB", description, amount])
        total_expenses += amount
    expense_rows.append(["", "TOTAL EXPENSES", total_expenses])

    # Create final total row
    final_total = round(total_amount - discount - commission - total_expenses, 4)
    # final_total = round(final_amount, 4)
    final_total_row = ["", "FINAL TOTAL", final_total]

    # Generate table
    header = f"**Driver Name:** {driver_name}\n**Line:** {line}\n**Date:** {date}\n\n"
    table = tabulate(
        table_rows + summary_rows + expense_rows + [final_total_row],
        headers=["", "Product", "Amount"],
        tablefmt="grid",
        maxcolwidths=[None, 10, None],
    )
    telegram_message = f"<pre>{header}{table}</pre>"

    return telegram_message


# data = [{"date": "2025-01-02","time":datetime.now().strftime("%H:%M:%S"), "driver_name": "Avudai amman agency", "line": "Karia patti", "product_name": "Mango 200ml PET", "base_amount": 200.0, "final_amount": 180.0, "discount": 0.0, "commission": 20.0, "kuraivu_cases": 0, "kuraivu_pieces": 0, "adhiga_varavu_cases": 0, "adhiga_varavu_pieces": 0, "expenses": [{"description": "Petrol", "amount": 0}, {"description": "Food", "amount": 0}], "total_expense": 0}, {"date": "2025-01-02", "driver_name": "Avudai amman agency", "line": "Kilavalavu", "product_name": "200ml color", "base_amount": 400.0, "final_amount": 350.0, "discount": 0.0, "commission": 50.0, "kuraivu_cases": 0, "kuraivu_pieces": 0, "adhiga_varavu_cases": 0, "adhiga_varavu_pieces": 0, "expenses": [{"description": "Petrol", "amount": 0}, {"description": "Food", "amount": 0}], "total_expense": 0}]

# print(format_msg(data) )
# asyncio.run(send_message(format_msg(data)))


class SheetInfo(BaseModel):
    date: str
    time: str 
    driver_name: str
    line: str
    product_name: str 
    base_amount: float
    final_amount: float
    discount: float
    commission: float
    kuraivu_cases: int
    kuraivu_pieces: int
    adhiga_varavu_cases: int
    adhiga_varavu_pieces: int 
    expenses: list[ dict[str, object] ]


app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logger.add("loguru.log")

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/update_sheet", methods=["POST"])
def update_sheet():
    request_data = request.data.decode("utf-8")
    logger.info(f"data is : {request_data}")
    if request_data is None:
        raise abort(400)

    data_json: list[dict[str, object]] = json.loads(request_data)["entries"]
    all_resp = []
    id = generate_id()
    for data in data_json:
        sheet_info = SheetInfo(**data)
        sheet_info_dict = sheet_info.model_dump()
        # sheet_info_dict["expenses"] = str( sheet_info_dict["expenses"] )
        sheet_info_dict["_id"] = id 
        resp = update_google_sheet(sheet_info_dict)
        all_resp.append(resp)

    try:
        update_on_telegram(all_resp) 
    except Exception as e:
        logger.error(e)

    return jsonify({"status":True})


def update_on_telegram(sheet_info: list):
    data = format_msg(sheet_info)
    
    resp = asyncio.run(send_message(data))
    logger.info(f"update performed on telegram: {resp}")

    return 


@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')





@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "GET":
        return render_template("upload.html")

    save_at = Path( "static/js/data.js" )
    if save_at.exists():
        save_at.rename("static/js/data_bkup.js")
    
    file = request.files["file"]
    file.save(str(save_at))

    resp = make_response()

    return resp 
