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
    credits = data.get("credits", {"payable": 0, "receivable": 0})
    
    # Get driver name, line, and date
    driver_name = entries[0]['driver_name']
    line = entries[0]['line']
    date = entries[0]['date']
    date_split = date.split("-")
    date = date_split[-1] + "-" + date_split[-2] + "-" + date_split[-3]

    # Create table rows for products and their base amounts
    table_rows = []
    for item in entries:
        product_name = f"{item['product_name']}"

        # Add sales info with base amount
        table_rows.append(["ADD", product_name + " " + f"{item['cases']}C / {item['pieces']}P", item["base_amount"]])
        total_amount += item["base_amount"]


        # Add goods upload/return info
        table_rows.append(["INFO", f"Goods Upload: {item['goods_upload_cases']}C / {item['goods_upload_pieces']}P", 0])
        table_rows.append(["INFO", f"Goods Return: {item['goods_return_cases']}C / {item['goods_return_pieces']}P", 0])
        
    # Add total before deductions
    table_rows.append(["", "Total Before Deductions", total_amount])
    table_rows.append(["", "---------------", "--------"])

    # Process all deductions
    deduction_rows = []
    for item in entries:
        # Add individual discounts
        for discount_entry in item.get('discount', []):
            discount_amount = (discount_entry['cases'] * discount_entry['size']) + (discount_entry['pieces'] * (discount_entry['size']/24))
            deduction_rows.append(["SUB", f"Discount ({discount_entry['size']}) - {item['product_name']}", discount_amount])
            discount += discount_amount

        # Add individual commissions
        for commission_entry in item.get('commission', []):
            commission_amount = (commission_entry['cases'] * commission_entry['size']) + (commission_entry['pieces'] * (commission_entry['size']/24))
            deduction_rows.append(["SUB", f"Commission ({commission_entry['size']}) - {item['product_name']}", commission_amount])
            commission += commission_amount

        if item.get("kuraivu_amount") is not None and item.get("kuraivu_amount") > 0:
            deduction_rows.append(["ADD", f"Kuraivu - {item['product_name']}", item["kuraivu_amount"]])
        
        final_amount += item["final_amount"]

    # Add total deductions summary
    summary_rows = [
        ["SUB", "Total Discount", discount],
        ["SUB", "Total Commission", commission],
    ]

    # Add credits
    if credits["payable"] > 0:
        summary_rows.append(["SUB", "Credit Payable", credits["payable"]])
    if credits["receivable"] > 0:
        summary_rows.append(["ADD", "Credit Receivable", credits["receivable"]])

    # Add total after deductions
    summary_rows.append(["", "Total After Deductions", final_amount])
    summary_rows.append(["", "---------------", "--------"])

    # Create expense rows
    expense_rows = []
    total_expenses = 0
    for description, amount in expenses.items():
        expense_rows.append(["SUB", description, amount])
        total_expenses += amount
    expense_rows.append(["", "Total Expenses", total_expenses])

    # Create final total row
    final_total = round(final_amount - total_expenses, 4)
    final_total_row = ["", "FINAL TOTAL", final_total]

    # Generate table
    header = f"**Driver Name:** {driver_name}\n**Line:** {line}\n**Date:** {date}\n\n"
    table = tabulate(
        table_rows + deduction_rows + summary_rows + expense_rows + [final_total_row],
        headers=["", "Description", "Amount"],
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
    order_id = generate_numeric_id(items_sheet_manager)

    # Handle expenses
    expense_sheet_info = ValidateExpenseInfo(
        transaction_id=order_id, 
        expenses=data_json["expenses"]
    )
    expense_sheet_info = ExpenseSheetHandler(expense_sheet_manager, expense_sheet_info)
    expense_rows = expense_sheet_info.compute_expense()
    total_expense = expense_sheet_info.total_expense

    # Add credits to total expense calculation
    credits = data_json.get("credits", {})
    credit_payable = credits.get("payable", 0)
    credit_receivable = credits.get("receivable", 0)
    total_expense = total_expense + credit_payable - credit_receivable

    # Handle product entries
    product_sheet_info = ValidateSheetInfo(
        transaction_id=order_id, 
        entries=data_json["entries"], 
        total_expense=total_expense
    )
    product_sheet_handler = ProductSheetHandler(items_sheet_manager, product_sheet_info)
    product_rows = product_sheet_handler.parse_product_entries()

    data_json["total_expense"] = total_expense    
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as exec:
        future1 = exec.submit(expense_sheet_info.add_expense_row, expense_rows)
        future2 = exec.submit(product_sheet_handler.add_product_row, product_rows)
        future3 = exec.submit(update_on_telegram, data_json)

    return jsonify({"status": True})



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