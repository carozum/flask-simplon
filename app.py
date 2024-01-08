# Virtual Env : env_flask_simplon
from flask import Flask, render_template, request


app = Flask(__name__)


# @app.route('/')  # request
# def index():
#     return "hello World !"  # response

@app.route('/')
def index():
    message = "Bienvenue dans la page de test de Flask dans le cadre de la formation Microsoft IA by Simplon"
    return render_template(
        "index.html",
        message=message)


@app.route('/', methods=['POST'])
def text_box():
    text = request.form['username']
    processed_text = text.upper()
    return render_template("bienvenue.html", message=processed_text)


@app.route('/page2')
def page2():
    return render_template('page2.html')


if __name__ == '__main__':
    app.run(debug=True, port=8000, host='127.0.0.1')
