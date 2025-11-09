from typing import List
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass

class Drivers(Base):
    __tablename__ = "drivers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"{self.name}"


class Lines(Base):
    __tablename__ = "lines"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"{self.name}"



class Expenses(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))

    def __repr__(self):
        return f"{self.name}"


class Products(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    max_case_count: Mapped[int] = mapped_column()
    kuraivu: Mapped[int] = mapped_column()

    # One-to-many relationship
    commissions: Mapped[list["Commissions"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"  # optional: deletes related commissions if product deleted,
    )

    # One-to-many relationship
    discounts: Mapped[list["Discounts"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"  # optional: deletes related commissions if product deleted
    )

    gains: Mapped[list["Gains"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"  # optional: deletes related commissions if product deleted
    )

    price: Mapped["Prices"] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",  # optional: deletes related commissions if product deleted,
        uselist=False
    )


    def __repr__(self):
        return f"{self.name}"


class Commissions(Base):
    __tablename__ = "commissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    case: Mapped[float]
    piece: Mapped[float]
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    # Many-to-one relationship
    product: Mapped["Products"] = relationship(back_populates="commissions")

    def __repr__(self):
        return f"C:{self.case}, P:{self.piece}"


class Discounts(Base):
    __tablename__ = "discounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    case: Mapped[float]
    piece: Mapped[float]

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    # Many-to-one relationship
    product: Mapped["Products"] = relationship(back_populates="discounts")

    def __repr__(self):
        return f"C:{self.case}, P:{self.piece}"


class Gains(Base):
    __tablename__ = "gains"

    id: Mapped[int] = mapped_column(primary_key=True)
    case: Mapped[float]
    piece: Mapped[float]

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    # Many-to-one relationship
    product: Mapped["Products"] = relationship(back_populates="gains")

    def __repr__(self):
        return f"C:{self.case}, P:{self.piece}"


class Prices(Base):
    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(primary_key=True)
    case: Mapped[float]
    piece: Mapped[float]


    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    # Many-to-one relationship
    product: Mapped["Products"] = relationship(back_populates="price")

    def __repr__(self):
        return f"C:{self.case}, P:{self.piece}"
