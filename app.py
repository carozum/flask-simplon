from flask import Flask, render_template, request, redirect
from models import db, User, app, Log_u
from dotenv import dotenv_values
import requests
import json
import numpy as np
import pandas as pd


# Eléments pour l'API https://devapi.ai/
config = dotenv_values(".env")
AUTH_KEY = config['API_KEY']
AUTH_KEY_2 = config['API_KEY_chart']
url_news = 'https://devapi.ai/api/v1/markets/news'
url_quotes = 'https://devapi.ai/api/v1/markets/quote'


""" Fonction qui permet de transformer un nom de company saisi en entréé par l'utilisateur
en un ticker utilisé en entrée pour la requête API"""


def trouver_ticker(company):
    df = pd.read_csv('ticker.csv', sep=';')
    df['Name'] = df['Name'].str.lower()
    search = df[df['Name'].str.contains(company.lower())].head(1).Symbol
    return search.values[0]


""" Fonction qui permet à partir d'un ticker et d'une URL d'API de charger un json
utilisé comme dictionnaire python"""


def trouver_api(ticker, url):
    params = {'ticker': ticker}
    headers = {'Authorization': f'Bearer {AUTH_KEY}'}
    response = requests.request('GET', url, headers=headers, params=params)
    return response.json()


""" Fonction qui prend un dataframe en entrée et sort les statistiques de base"""


def compute_statistics(data):
    statistics = {
        'Nombre de lignes': len(data),
        'Nombre de colonnes': len(data.columns),
        'Moyenne': data.mean().to_dict(),
        'Écart-type': data.std().to_dict(),
        'Valeurs manquantes': data.isnull().sum().to_dict(),
    }
    return statistics


""" route index avec formulaire aboutit à la création d'un message personnalisé
et d'une liste de news concernant une société donnée par l'utilisateur 
ainsi que sa quotation boursière"""


@app.route('/', methods=['POST', 'GET'])
def index():
    # TRAVAIL SUR LE USER

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

        # TRAVAIL SUR LA COMPANY

        if company is not None:
            try:
                # Etape 3 : cas ou la company existe
                ticker = trouver_ticker(company)
                # Etape 4 : sortir de l'API les news concernant le ticker (symbol) demandé
                news = trouver_api(ticker, url_news)
                # Etape 5 : sortir de l'API les chiffres de valorisation du symbol demandé
                quotes = trouver_api(ticker, url_quotes)
                print(quotes)
                # Etape 6 : enregistrer le log dans la base de donnée
                user = request.form['pseudo']
                saisie = request.form['companyName']
                symbol = ticker
                company = quotes['body']['companyName']
                exchange = quotes['body']['exchange']
                lastSalePrice = quotes['body']['primaryData']['lastSalePrice']
                volume = quotes['body']['primaryData']['volume']
                percentageChange = quotes['body']['primaryData']['percentageChange']
                new_log = Log_u(user=user,
                                created=None,
                                saisie=saisie,
                                symbol=symbol,
                                company=company,
                                exchange=exchange,
                                lastSalePrice=lastSalePrice,
                                volume=volume,
                                percentageChange=percentageChange)
                db.session.add(new_log)
                db.session.commit()

                return render_template('bienvenue.html', message=message, news=news, quotes=quotes, company=company)

            # Etape 3 Bis : cas ou la company n'existe pas
            except IndexError:

                # Etape 4 Bis :  news est un dictionnaire vide
                news = {}
                # Etape 5 Bis : quotes est une dictionnaire vide
                quotes = {}
                # Etape 6 Bis : enregistrer le log dans la base de données
                user = request.form['pseudo']
                saisie = request.form['companyName']
                symbol = 'N/A'
                company = 'N/A'
                exchange = 'N/A'
                lastSalePrice = 'N/A'
                volume = 'N/A'
                percentageChange = 'N/A'
                new_log = Log_u(user=user,
                                created=None,
                                saisie=saisie,
                                symbol=symbol,
                                company=company,
                                exchange=exchange,
                                lastSalePrice=lastSalePrice,
                                volume=volume,
                                percentageChange=percentageChange)
                db.session.add(new_log)
                db.session.commit()

                return render_template('bienvenue.html', message=message, news=news, quotes=quotes)

    return render_template('index.html')


""" Route qui permet d'afficher le contenu de la table User"""


@app.route('/utilisateurs-inscrits')
def utilisateurs_inscrits():
    users = User.query.all()
    return render_template("utilisateurs-inscrits.html", users=users)


""" Route qui permet d'afficher le contenu de la table Log_u"""


@app.route('/logs.html')
def logs():
    logs = Log_u.query.all()
    return render_template("logs.html", logs=logs)


""" Route qui affiche un formulaire pemettant à l'utilisateur de uploader un fichier"""


@app.route('/form-file', methods=['GET', 'POST'])
def form_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            return redirect(request.url)

        if file:
            try:
                if file.filename.endswith('.csv'):
                    data = pd.read_csv(file)
                elif file.filename.endswith(('.xls', '.xlsx')):
                    data = pd.read_excel(file)
                else:
                    return render_template('error.html', message='Format de fichier non pris en charge.')

                statistics = compute_statistics(data)
                return render_template('statistiques.html', statistics=statistics)

            except Exception as e:
                return render_template('error.html', message=f'Une erreur s\'est produite : {str(e)}')

    return render_template('form-file.html')


@app.route('/statistiques')
def statistiques():
    return render_template('statistiques.html')


url_chart = 'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=IBM&apikey=demo'
r = requests.get(url_chart)
data = r.json()


@app.route('/form-chart', methods=['POST', 'GET'])
def form_chart():
    if request.method == 'POST':
        api_key = AUTH_KEY_2
        try:
            saisie = request.form['companyName']
            symbol = trouver_ticker(saisie)
            endpoint = f'https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY_ADJUSTED&symbol={symbol}&apikey={api_key}'

            response = requests.get(endpoint)
            data = response.json()

            # Créez le graphique
            dates = list(data['Monthly Adjusted Time Series'].keys())
            prices = [float(data['Monthly Adjusted Time Series']
                            [date]['4. close']) for date in dates]
            print(dates)
            print(prices)

            message = "Voici votre graph"
            return render_template('chart.html', message=message, dates=dates, prices=prices, symbol=symbol)

        except IndexError:
            image = None
            print('hello')
            message = "rien à ce nom"
            return render_template('chart.html', message=message, dates=[], prices=[], symbol=symbol)

    return render_template('form-chart.html')


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

 # # Create a Plotly Express line chart

 # import plotly
# import plotly.express as px
# import io
# import base64
# fig = px.line(x=dates, y=prices, labels={'x': 'Date', 'y': 'Stock Price'},
#               title=f'Stock Price Over Time - {symbol}')

# # Save the figure to a BytesIO object
# img_stream = io.BytesIO()
# fig.write_image(img_stream, format='png')
# img_stream.seek(0)

# # Convert the image to base64 for embedding in HTML
# img_base64 = base64.b64encode(img_stream.read()).decode('utf-8')
