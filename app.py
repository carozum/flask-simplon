from flask import Flask, render_template, request
from models import db, User, app


def add_user_if_not_exists(prenom, nom, sexe, pseudo, titre):
    existing_user = User.query.filter_by(pseudo=pseudo).first()

    if existing_user is None:
        new_user = User(prenom=prenom, nom=nom, sexe=sexe,
                        pseudo=pseudo, titre=titre)
        db.session.add(new_user)
        db.session.commit()
        return "User added successfully."
    else:
        return "User already exists."


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        prenom = request.form['prenom']
        nom = request.form['nom']
        sexe = request.form['sexe']
        pseudo = request.form['pseudo']
        titre = "Mr" if sexe == "homme" else "Mme"

        new_user = User(prenom=prenom,
                        nom=nom,
                        sexe=sexe,
                        pseudo=pseudo,
                        titre=titre)
        db.session.add(new_user)
        db.session.commit()

        message = f"Bonjour {titre} {prenom} {nom}, votre nom d'utilisateur est {pseudo}"
        return render_template('bienvenue.html', message=message)

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
