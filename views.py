from flask import Flask, Request, request, jsonify
from flask import render_template
from sheet import update_google_sheet
from pydantic import BaseModel, Field
from datetime import datetime
from flask_cors import CORS
from flask import abort
import json
from notify_telegram import send_message
import asyncio 
from loguru import logger
from utils import parse_expense,generate_id



def format_msg(sheet_info: list):
    prod_count = 1
    msg = ""
    for prod in sheet_info:
        msg += f"{prod_count}."
        
        for key, val in prod.items():
            if key != "expenses":
                msg += f"    {key.replace('_', ' ').title()}  : {prod[key]}\n"

        prod_count += 1

        msg += "\n\n"
    

    msg += "\n     Expenses:\n"
    msg += "----------------------------------\n"
    exp = parse_expense(prod)
    if exp is None:
        msg += f"         No Expenses added\n"
    else:
        for exp_key, exp_val in exp.items():
            msg += f"         {exp_key.replace('_', ' ').title()} : {exp_val}\n"
        
    msg += "\n\n"
        
        

    return msg 

class SheetInfo(BaseModel):
    date: str
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
        print(sheet_info_dict)
        sheet_info_dict["_id"] = id 
        resp = update_google_sheet(sheet_info_dict)
        all_resp.append(resp)

    try:
        update_on_telegram(all_resp)
    except Exception as e:
        pass 

    return jsonify({"status":True})


def update_on_telegram(sheet_info: list):
    sheet_msg_formated = format_msg(sheet_info)

    resp = asyncio.run( send_message(sheet_msg_formated ))
    return jsonify({"status": True})


@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')