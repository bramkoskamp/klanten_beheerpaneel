import sqlalchemy as sa
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Customer(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    full_name = sa.Column(sa.String, nullable=False)
    email = sa.Column(sa.String, nullable=False)
    phone_number = sa.Column(sa.String, nullable=False)
    adress = sa.Column(sa.String, nullable=False)


class Service(db.Model):
    id = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
    name = sa.Column(sa.String, nullable=False)
    price = sa.Column(sa.Float, nullable=False)
    description = sa.Column(sa.String, nullable=True)
