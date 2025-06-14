from flask import Flask, render_template
from flask_cors import CORS  
from flask_swagger_ui import get_swaggerui_blueprint

# Inicialize o Firebase antes de qualquer outro import que dependa dele
from firebase_init import initialize_firebase
firebase_app = initialize_firebase()

# Agora sim, pode importar os Controllers
from Controllers.Usuario_Controller import usuario_bp
from Controllers.Esporte_Controller import esporte_bp
from Controllers.Eventos_Controller import evento_bp
from Controllers.Post_Controller import postagem_bp
from Controllers.Comentario_Controller import comentario_bp
from Controllers.Treino_Controller import treino_bp

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

@app.route('/')
def index():
    return "Conectado! Inicie o Live Server em um View para testar"

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)