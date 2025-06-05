from flask import Flask,  render_template
from firebase_admin import credentials, initialize_app, get_app
from Controllers.Usuario_Controller import usuario_bp
from Controllers.Esporte_Controller import esporte_bp
from Controllers.Eventos_Controller import evento_bp
from Controllers.Post_Controller import postagem_bp
from Controllers.Comentario_Controller import comentario_bp
from Controllers.Treino_Controller import treino_bp
from flask_swagger_ui import get_swaggerui_blueprint

from flask_cors import CORS  


app = Flask(__name__, template_folder='Views')
CORS(app)

SWAGGER_URL = '/swagger'  
API_URL = '/static/swagger.yaml' 

swaggerui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={ 'app_name': "MoveHive APIs" }
)

app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

app.register_blueprint(usuario_bp)
app.register_blueprint(esporte_bp)
app.register_blueprint(evento_bp)
app.register_blueprint(postagem_bp)
app.register_blueprint(comentario_bp)
app.register_blueprint(treino_bp)

try:
    firebase_app = get_app()  
except ValueError:
    cred = credentials.Certificate("move-hive-firebase-adminsdk-fbsvc-0334323fd4.json")
    firebase_app = initialize_app(cred)



@app.route('/')
def index():
    return "Conectado! Inicie o Lives Server em um View para testar"


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
