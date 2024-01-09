from flask import Flask, render_template, request
from models import db, User, app
from dotenv import dotenv_values
import requests
import json
import numpy as np
import pandas as pd


config = dotenv_values(".env")
AUTH_KEY = config['API_KEY']
url_news = 'https://devapi.ai/api/v1/markets/news'
url_quotes = 'https://devapi.ai/api/v1/markets/quote'


def trouver_ticker(company):
    df = pd.read_csv('ticker.csv', sep=';')
    df['Name'] = df['Name'].str.lower()
    search = df[df['Name'].str.contains(company.lower())].head(1).Symbol

    return search.values[0]


def trouver_api(ticker, url):
    params = {'ticker': ticker}
    headers = {'Authorization': f'Bearer {AUTH_KEY}'}
    response = requests.request('GET', url, headers=headers, params=params)
    return response.json()


@app.route('/', methods=['POST', 'GET'])
def index():
    # Etape 1 - Recueil des données du formulaire
    if request.method == 'POST':
        prenom = request.form['prenom']
        nom = request.form['nom']
        sexe = request.form['sexe']
        pseudo = request.form['pseudo']
        titre = "Mr" if sexe == "homme" else "Mme"
        company = request.form['companyName']
        message = f"Bonjour {titre} {prenom} {nom}, votre nom d'utilisateur est {pseudo}."

        # Etape 2 - Vérification que le pseudo n'est pas déjà dans la base
        users = User.query.all()
        pseudo_list = []
        for user in users:
            pseudo_list.append(user.pseudo)

        # Etape 2 - le cas échéant ajout de l'utilisateur dans la base
        if pseudo not in pseudo_list:
            new_user = User(prenom=prenom,
                            nom=nom,
                            sexe=sexe,
                            pseudo=pseudo,
                            titre=titre)
            db.session.add(new_user)
            db.session.commit()

        if pseudo in pseudo_list:
            message += " Vous êtes déjà inscrit sur le site."

        # Etape 3 - convertir la company recherchée en ticker
        if company is not None:
            try:
                ticker = trouver_ticker(company)
                # sortir de l'API les news concernant le ticker (symbol) demandé
                news = trouver_api(ticker, url_news)
                # sortir de l'API les chiffres de valorisation du symbol demandé
                quotes = trouver_api(ticker, url_quotes)
                return render_template('bienvenue.html', message=message, news=news, quotes=quotes, company=company)
            except IndexError:
                news = {}
                quotes = {}
                return render_template('bienvenue.html', message=message, news=news, quotes=quotes)

            # enregistrer le log dans la base de donnée

    return render_template('index.html')


@app.route('/utilisateurs-inscrits')
def utilisateurs_inscrits():
    users = User.query.all()
    return render_template("utilisateurs-inscrits.html", users=users)


@app.route('/about')
def about():
    return render_template('about.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True, port=8000, host='127.0.0.1')


# existing_user = User.query.filter_by(pseudo=pseudo).first()
        # if existing_user is None:
        #     new_user = User(prenom=prenom, nom=nom, sexe=sexe,
        #                 pseudo=pseudo, titre=titre)
        #     db.session.add(new_user)
        #     db.session.commit()
        #     return render_template('bienvenue.html', message=message)
        # else:
        #     return render_template('index.html')
