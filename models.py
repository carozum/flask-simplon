from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    prenom = db.Column('Prenom', db.String())
    nom = db.Column('Nom', db.String())
    sexe = db.Column('Sexe', db.String())
    pseudo = db.Column('Pseudo', db.String())
    titre = db.Column('Titre', db.String())


class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column('User', db.String())
    date = db.Column('Date', db.DateTime,
                     default=datetime.datetime.now)
    saisie = db.Column('Saisie', db.String())
    symbol = db.Column('Symbol', db.String())
    company = db.Column('Company', db.String())
    exchange = db.Column('Exchange', db.String())
    lastSalePrice = db.Column('Price', db.String())
