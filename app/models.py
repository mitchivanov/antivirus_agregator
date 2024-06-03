from app import db
from sqlalchemy.dialects.postgresql import JSON

class Threat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    damage = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

class AntivirusProgram(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    efficacy = db.Column(JSON, nullable=False)
    description = db.Column(db.Text, nullable=True)
    type = db.Column(db.String(50), nullable=False)  # Новый столбец для типа программы (антивирус, межсетевой экран, антивирусная утилита)
