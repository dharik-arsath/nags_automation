from flask import Flask, request, jsonify, make_response
from flask import render_template
# from sheet import update_google_sheet
from flask_cors import CORS
from flask import abort
import json
from notify_telegram import send_message
import asyncio
from loguru import logger
from utils import generate_id
from pathlib import Path

from tabulate import tabulate
from sheets.sheet import ProductSheetHandler
from sheets.sheet_dto import ValidateSheetInfo, ValidateExpenseInfo
from sheets.expense_sheet import ExpenseSheetHandler
from sheets.sheet_helper import authenticate, get_numeric_id_from_main_sheet

gc = authenticate()


def format_msg(data):
    # Initialize variables
    total_amount = 0
    discount = 0
    commission = 0
    final_amount = 0
    expenses = {}
    entries = data["entries"]
    expenses = data["expenses"]
    
    # Get driver name, line, and date
    driver_name = entries[0]['driver_name']
    line = entries[0]['line']
    date = entries[0]['date']

    # Create table rows
    table_rows = []
    additional_amount = 0
    for item in entries:
        product_name = f"{item['product_name']}"
        table_rows.append(["ADD", product_name, item["base_amount"]])
        print("*" * 20)
        if item.get("kuraivu_amount") is not None and item.get("kuraivu_amount") > 0:
            table_rows.append(["ADD", "kuraivu", item["kuraivu_amount"]])
            additional_amount += item["kuraivu_amount"]
        total_amount += item["base_amount"] + additional_amount
        discount += item["discount"]
        commission += item["commission"]
        final_amount += item["final_amount"]
        additional_amount = 0

    # Create summary rows
    summary_rows = [
        ["", "Total", total_amount],
        ["SUB", "DISCOUNT", discount],
        ["SUB", "COMMISSION", commission],
        ["", "TOTAL", round(final_amount - additional_amount, 4)],
    ]

    # Create expense rows
    expense_rows = []
    total_expenses = 0
    for description, amount in expenses.items():
        expense_rows.append(["SUB", description, amount])
        total_expenses += amount
    expense_rows.append(["", "TOTAL EXPENSES", total_expenses])

    # Create final total row
    final_total = round(final_amount  - total_expenses, 4)
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

    data_json: list[dict[str, object]] = json.loads(request_data)
    # transaction_id        = generate_id()
    order_id              = get_numeric_id_from_main_sheet(gc)

    expense_sheet_info    = ValidateExpenseInfo(transaction_id=order_id, expenses=data_json["expenses"])
    expense_sheet_info    = ExpenseSheetHandler(gc, expense_sheet_info)
    expense_sheet_info.add_expense_row()
    total_expense         = expense_sheet_info.total_expense

    
    product_sheet_info    = ValidateSheetInfo(transaction_id=order_id, entries=data_json["entries"], total_expense=total_expense)
    product_sheet_handler = ProductSheetHandler(gc, product_sheet_info)
    product_sheet_handler.add_product_row()


    data_json["total_expense"] = total_expense

    try:
        update_on_telegram(data_json) 
    except Exception as e:
        logger.error(e)

    return jsonify({"status":True})



def update_on_telegram(sheet_info: list):
    try:
        data = format_msg(sheet_info)
        resp = asyncio.run(send_message(data))
        logger.info(f"update performed on telegram: {resp}")

    except Exception as e:
        logger.error(f"Error updating on telegram: {e}")


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
