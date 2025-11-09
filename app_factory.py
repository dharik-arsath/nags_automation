from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_cors import CORS
from flask import Flask
from data_views import data_bp
from database import db_session as session
import secrets


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = secrets.token_urlsafe(32)
    app.register_blueprint(data_bp)
    CORS(app)  # Enable CORS for all routes

    from models import (
        Products,
        Drivers,
        Lines,
        Expenses,
        Prices,
        Gains,
        Commissions,
        Discounts,
    )

    admin = Admin()
    admin.init_app(app)

    admin.add_view(ModelView(Drivers, session))
    admin.add_view(ModelView(Expenses, session))
    admin.add_view(ModelView(Lines, session))
    admin.add_view(ModelView(Commissions, session))
    admin.add_view(ModelView(Discounts, session))
    admin.add_view(ModelView(Gains, session))
    admin.add_view(ModelView(Prices, session))

    class ProductView(ModelView):
        column_list = [
            "name",
            "max_case_count",
            "kuraivu",
            "price",
            "commissions",
            "discounts",
            "gains",
        ]

    admin.add_view(ProductView(Products, session))

    return app
