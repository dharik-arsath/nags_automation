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
    base_amount: float
    final_amount: float
    discount: float
    commission: float
    kuraivu: int
    adhiga_varavu: int
    diesel: float
    vehicle_damage: float
    other_expense: float
    other_expense_description: str = Field(default="")


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
        print(data)
        sheet_info = SheetInfo(**data)
        print(sheet_info.model_dump())
        update_google_sheet(sheet_info.model_dump())

    return jsonify({"status":True})
