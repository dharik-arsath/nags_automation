from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from models import Products, Expenses, Drivers, Lines


class DB_DAO:
    def __init__(self, session: Session):
        self.session = session

    def get_products(self):
        stmt = self.session.query(Products).options(
            selectinload(Products.commissions),
            selectinload(Products.gains),
            selectinload(Products.discounts),
            selectinload(Products.price),
        )
        result = stmt.all()  # query objects directly, no need for scalars() here
        return result

    def get_all_expenses(self):
        stmt = select(Expenses)
        return self.session.scalars(stmt).all()

    def get_drivers(self):
        stmt = select(Drivers)
        return self.session.scalars(stmt).all()

    def get_lines(self):
        stmt = select(Lines)
        return self.session.scalars(stmt).all()
