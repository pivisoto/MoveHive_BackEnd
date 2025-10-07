from flask import Flask, render_template, request
from flask_cors import CORS  
from flask_swagger_ui import get_swaggerui_blueprint
from flask_caching import Cache
from utils.cache import set_cache_instance

from firebase_init import initialize_firebase
firebase_app = initialize_firebase()

from Controllers.Usuario_Controller import usuario_bp
from Controllers.Esporte_Controller import esporte_bp
from Controllers.Eventos_Controller import evento_bp
from Controllers.Post_Controller import postagem_bp
from Controllers.Comentario_Controller import comentario_bp
from Controllers.Treino_Controller import treino_bp
from Controllers.Notificacao_Controller import notificacao_bp
from Controllers.UsuarioEmpresa_Controller import usuarioEmpresa_bp
from Controllers.Hive_controller import hive_bp


app = Flask(__name__, template_folder='Views/Social_media')
CORS(app)

SWAGGER_URL = '/swagger'  
API_URL = '/static/swagger.yaml' 

swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL,API_URL,config={ 'app_name': "MoveHive APIs" })

cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': f'redis://localhost:6379'})
set_cache_instance(cache)


app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)
app.register_blueprint(usuario_bp)
app.register_blueprint(esporte_bp)
app.register_blueprint(evento_bp)
app.register_blueprint(postagem_bp)
app.register_blueprint(comentario_bp)
app.register_blueprint(treino_bp)
app.register_blueprint(notificacao_bp)
app.register_blueprint(usuarioEmpresa_bp)
app.register_blueprint(hive_bp)

@app.route('/')
def index():
    return "Conectado! Inicie o Live Server em um View para testar"



@app.route('/usuario/resetar-senha', methods=['GET'])
def pagina_reset_senha():
    token = request.args.get('token')  # pega o token da URL
    return render_template('resetSenha.html', token=token)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)