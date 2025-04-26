from flask import Flask,  render_template
from firebase_admin import credentials, initialize_app, get_app
from Controllers.Usuario_Controller import usuario_bp
from Controllers.Esporte_Controller import esporte_bp
from Controllers.Eventos_Controller import evento_bp
from flask_cors import CORS  


app = Flask(__name__, template_folder='Views')
CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500"}})


try:
    firebase_app = get_app()  
except ValueError:
    cred = credentials.Certificate("move-hive-firebase-adminsdk-fbsvc-0334323fd4.json")
    firebase_app = initialize_app(cred)


app.register_blueprint(usuario_bp)
app.register_blueprint(esporte_bp)
app.register_blueprint(evento_bp)


@app.route('/')
def index():
    return "Conectado! Inicie o Lives Server em um View para testar"


if __name__ == '__main__':
    app.run(debug=True)
