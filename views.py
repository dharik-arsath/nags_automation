from flask import Flask, Request, request, jsonify
from flask import render_template
from sheet import update_google_sheet
from pydantic import BaseModel, Field
from datetime import datetime
from flask_cors import CORS
from flask import abort
import json



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
    print("---------------------------------------------------------------")
    data = request.data.decode("utf-8")
    print(data)
    if data is None:
        raise abort(400)

    data_json: list[dict[str, object]] = json.loads(data)["entries"]
    for data in data_json:
        sheet_info = SheetInfo(**data)
        sheet_info_dict = sheet_info.model_dump()
        # sheet_info_dict["expenses"] = str( sheet_info_dict["expenses"] )
        print(sheet_info_dict)
        update_google_sheet(sheet_info_dict)

    return jsonify({"status":True})
