from flask import Flask, render_template, request, redirect, jsonify, session
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from models import db, User, app, Log_u
from dotenv import dotenv_values
from PIL import Image
import requests
import numpy as np
import pandas as pd
import numpy as np
import io
import re
import base64
import secrets

app.secret_key = secrets.token_hex(16)

# Eléments pour l'API https://devapi.ai/
config = dotenv_values(".env")
AUTH_KEY = config['API_KEY']
AUTH_KEY_2 = config['API_KEY_chart']
url_news = 'https://devapi.ai/api/v1/markets/news'
url_quotes = 'https://devapi.ai/api/v1/markets/quote'


# chargement du modèle MNIST de reconnaissance des digits
model = load_model('model_mnist.h5')


"""Function responsible for preparing the image before feeding the model"""


def preprocess_image(file):
    try:
        img_content = file.read()
        img = image.load_img(io.BytesIO(img_content),
                             target_size=(28, 28), color_mode='grayscale')
        img_array = image.img_to_array(img)
        img_array = np.expand_dims(img_array, axis=0)
        img_array /= 255.0
        return img_array
    except Exception as e:
        print(f"Error processing image: {e}")
        return None


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
        # company = request.form['companyName']
        message = f"Bonjour {titre} {prenom} {nom} ({pseudo})! "

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
            message += " Ravie de vous revoir sur le site."

        session['pseudo'] = pseudo
        return render_template('bienvenue.html', message=message)

    return render_template('index.html')


"""Route qui affiche la page de bienvenue"""


@app.route('/bienvenue')
def bienvenue():
    return render_template("bienvenue.html", message="Accueil du site")


"""" Route qui affiche les possibilités une fois connecté """


@app.route('/infos-company', methods=['POST', 'GET'])
def infos_company():

    if request.method == 'POST':
        saisie = request.form['companyName']

        if saisie is not None:
            try:
                # Etape 3 : cas ou la company existe
                ticker = trouver_ticker(saisie)
                # Etape 4 : sortir de l'API les news concernant le ticker (symbol) demandé
                news = trouver_api(ticker, url_news)
                # Etape 5 : sortir de l'API les chiffres de valorisation du symbol demandé
                quotes = trouver_api(ticker, url_quotes)
                print(quotes)
                # Etape 6 : enregistrer le log dans la base de donnée
                user = session['pseudo']
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

                return render_template('resultat-company.html', news=news, quotes=quotes, company=company)

            # Etape 3 Bis : cas ou la company n'existe pas
            except IndexError:
                # Etape 4 Bis :  news est un dictionnaire vide
                news = {}
                # Etape 5 Bis : quotes est une dictionnaire vide
                quotes = {}
                # Etape 6 Bis : enregistrer le log dans la base de données
                user = session['pseudo']
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

                return render_template('resultat-company.html', news=news, quotes=quotes, company="")

    return render_template('infos-company.html', news={}, quotes={}, company="")


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
                # Create HTML table for data.info()

                statistics = compute_statistics(data)

                # Create HTML table for data.describe()
                describe_table = data.describe().transpose().to_html()

                return render_template('statistiques.html', statistics=statistics, describe_table=describe_table)

            except Exception as e:
                return render_template('error.html', message=f'Une erreur s\'est produite : {str(e)}')

    return render_template('form-file.html', )


"""Route pour afficher les statistiques du fichier. A ajouter le traiment différent des données numériques ou textuelles"""


@app.route('/statistiques')
def statistiques():
    return render_template('statistiques.html')


"""Route to display the interactive chart using plotly express"""


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
            message = "rien à ce nom"
            return render_template('chart.html', message=message, dates=[], prices=[], symbol=symbol)

    return render_template('form-chart.html')


"""Route pour permettre à l'utilisateur de télécharger un fichier de digit"""


@app.route('/feed-model.html', methods=['POST', 'GET'])
def feed_model():

    if request.method == 'POST':
        # Get the uploaded image from the form
        file = request.files["file"]

        if file:
            try:
                img_array = preprocess_image(file)
                prediction = model.predict(img_array)
                result = np.argmax(prediction)
                return render_template("result-model.html", message="Prédiction: {}".format(result))
            except Exception as e:
                print(f"Error processing image: {e}")
                message = "Error"
                return render_template('result-model.html', message=message)

    return render_template('feed-model.html', message="Téléchargez une image de chiffre à prédire.")


@app.route('/draw', methods=['GET', 'POST'])
def draw():
    prediction = None

    if request.method == 'POST':
        url = request.form['url']

        # Extract base64 data from the URL
        image_data = re.sub('^data:image/.+;base64,', '', url)
        image_data = image_data.encode('utf-8')

        # Convert base64 data to image
        img = Image.open(io.BytesIO(base64.b64decode(image_data))).convert('L')
        img = img.resize((28, 28))
        img_array = np.array(img) / 255.0
        img_array = np.reshape(img_array, (1, 28, 28, 1))

        # Make prediction
        predictions = model.predict(img_array)
        predicted_class = np.argmax(predictions)

        # Convert to int if needed
        prediction = int(predicted_class)
        print(prediction)
        session['prediction'] = prediction

    return render_template('draw.html', prediction=prediction)


@app.route('/predict')
def predict():
    # Retrieve the prediction from the session
    prediction = session.get('prediction', None)

    return render_template('predict.html', prediction=prediction)


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
