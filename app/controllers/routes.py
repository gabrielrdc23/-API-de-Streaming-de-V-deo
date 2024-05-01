from flask import Flask, request, jsonify, Blueprint
from firebase_admin import auth, initialize_app
import os
from dotenv import load_dotenv
import json
import requests
from datetime import datetime
from app.models.models import User, Titulos, Historico, Lista_reproducao, Lista_reproducao_titulos, Generos

load_dotenv()
app = Flask(__name__)
firebase_app = initialize_app()

auth_bp = Blueprint('auth', __name__)
user_bp = Blueprint('user', __name__)
content_bp = Blueprint('content', __name__)

def verify_token():
    id_token = request.headers.get('Authorization')
    if not id_token:
        return jsonify({'error': 'Token não fornecido'}), 401

    try:
        decoded_token = auth.verify_id_token(id_token)
        request.uid = decoded_token['uid']
    except auth.InvalidIdTokenError:
        return jsonify({'error': 'Token inválido'}), 401
    except auth.ExpiredIdTokenError:
        return jsonify({'error': 'Token expirado'}), 401

@app.before_request
def before_request_func():
    if request.endpoint not in ['auth.signup', 'auth.login']:
        return verify_token()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    email, password, name = data['email'], data['password'], data['name']
    try:
        user_record = auth.create_user(email=email, password=password)
        new_user = User(email=email, name=name, data_criacao=str(datetime.now()))
        new_user.save()
        return jsonify({"message": "User created successfully", "firebase_uid": user_record.uid}), 201
    except Exception as e:
        if user_record:
            auth.delete_user(user_record.uid)
        return jsonify({"error": str(e)}), 400

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    response = requests.post(
        f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={os.getenv('FIREBASE_API_KEY')}",
        headers={'Content-Type': 'application/json'},
        json={"email": data['email'], "password": data['password'], "returnSecureToken": True}
    )
    if response.status_code != 200:
        return jsonify({'error': 'Credenciais inválidas'}), 401
    json_response = response.json()
    return jsonify({
        'message': 'Login realizado com sucesso',
        'token': json_response['idToken'],
        'refreshToken': json_response['refreshToken']
    }), 200

@user_bp.route('/usuarios/<int:user_id>', methods=['GET'])
def get_usuario(user_id):
    usuario = User.query.get(user_id)
    if usuario:
        return jsonify({
            "id": usuario.id, "name": usuario.name, "email": usuario.email, "data_criacao": usuario.data_criacao
        }), 200
    return jsonify({"message": "Usuário não encontrado"}), 404

@content_bp.route('/titulos', methods=['POST'])
def criar_titulo():
    data = request.get_json()
    novo_titulo = Titulos(**data, data_criacao=datetime.now())
    novo_titulo.save()
    return jsonify({"message": "Título criado com sucesso"}), 201

@content_bp.route('/titulos', methods=['GET'])
def listar_titulos():
    titulos = Titulos.query.all()
    return jsonify([{ 
        "id": titulo.id, "titulo": titulo.titulo, "sinopse": titulo.sinopse,
        "elenco": titulo.elenco, "diretor": titulo.diretor, "ano_lancamento": titulo.ano_lancamento,
        "ava_media": titulo.ava_media
    } for titulo in titulos]), 200

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(user_bp, url_prefix='/user')
app.register_blueprint(content_bp, url_prefix='/content')

if __name__ == "__main__":
    app.run(debug=True)
