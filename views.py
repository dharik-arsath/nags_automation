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
    for data in data_json:
        sheet_info = SheetInfo(**data)
        sheet_info_dict = sheet_info.model_dump()
        # sheet_info_dict["expenses"] = str( sheet_info_dict["expenses"] )
        print(sheet_info_dict)
        resp = update_google_sheet(sheet_info_dict)
        all_resp.append(resp)

    try:
        update_on_telegram(all_resp)
    except Exception as e:
        pass 

    return jsonify({"status":True})


# def update_on_telegram(sheet_info: SheetInfo):
#     resp = asyncio.run( send_message(sheet_info.model_dump()) )
#     return jsonify({"status": True})

def update_on_telegram(sheet_info: list):
    resp = asyncio.run( send_message(sheet_info ))
    return jsonify({"status": True})


@app.route('/thankyou')
def thank_you():
    return render_template('thankyou.html')