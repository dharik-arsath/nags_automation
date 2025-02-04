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
from sheets.sheet_dto import ValidateSheetInfo, ValidateExpenseInfo, SheetManager
from sheets.expense_sheet import ExpenseSheetHandler
from sheets.sheet_helper import authenticate, get_numeric_id_from_main_sheet, get_sheet_by_id, get_workbook_by_id,generate_numeric_id
import concurrent.futures
from functools import lru_cache
import os 
from flask import send_file
from flask import Request

gc = authenticate()
workbook = get_workbook_by_id(gc, os.getenv("NAGS_WORKBOOK_ID"))
items_sheet    = get_sheet_by_id(workbook, os.getenv("ITEM_SHEET_ID"))
expense_sheet  = get_sheet_by_id(workbook, os.getenv("EXPENSE_SHEET_ID"))

items_sheet_manager   = SheetManager(gc=gc, spreadsheet=workbook, worksheet=items_sheet)
expense_sheet_manager = SheetManager(gc=gc, spreadsheet=workbook, worksheet=expense_sheet)

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
    date_split = date.split("-")
    date = date_split[-1] + "-" + date_split[-2] + "-" + date_split[-3]

    # Create table rows
    table_rows = []
    additional_amount = 0
    for item in entries:
        product_name = f"{item['product_name']}"
        table_rows.append(["ADD", product_name + " " + f"{item['cases']}C / {item['pieces']}P", item["base_amount"]])
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


@app.before_request
def before_request():
    logger.info(f"Request: {request.method} {request.url}")
    logger.info(f"Headers: {request.headers}")
    logger.info(f"data: {request.data}")
    return 


@app.route("/", methods=["GET"])
@lru_cache()
def index():
    return render_template("index.html")


@app.route("/update_sheet", methods=["POST"])
def update_sheet():
    request_data = request.data.decode("utf-8")
    logger.info(f"data is : {request_data}")
    if request_data is None:
        raise abort(400)

    data_json = json.loads(request_data)
    # transaction_id        = generate_id()
    # order_id              = get_numeric_id_from_main_sheet(gc)
    order_id              = generate_numeric_id(items_sheet_manager)

    expense_sheet_info    = ValidateExpenseInfo(transaction_id=order_id, expenses=data_json["expenses"])
    expense_sheet_info    = ExpenseSheetHandler(expense_sheet_manager, expense_sheet_info)
    expense_rows          = expense_sheet_info.compute_expense()
    total_expense         = expense_sheet_info.total_expense
    
    product_sheet_info    = ValidateSheetInfo(transaction_id=order_id, entries=data_json["entries"], total_expense=total_expense)
    print(product_sheet_info)
    product_sheet_handler = ProductSheetHandler(items_sheet_manager, product_sheet_info)
    product_rows          = product_sheet_handler.parse_product_entries()

    
    data_json["total_expense"] = total_expense    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as exec:
        future1 = exec.submit(expense_sheet_info.add_expense_row, expense_rows)
        future2 = exec.submit(product_sheet_handler.add_product_row, product_rows)
        future3 = exec.submit(update_on_telegram, data_json)


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


@app.route("/download", methods=["GET"])
def download():
    path_at = Path("static/js/data.js")
    if not path_at.exists():
        resp = make_response()
        resp.status_code = 404
        return resp 
    
    
    resp = send_file(str(path_at),as_attachment=True)
    return resp 


@app.route("/health", methods=["GET"])
async def health():
    return jsonify({"status":True})