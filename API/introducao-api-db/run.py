from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Definição do Modelo de Dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    playlists = db.relationship('Playlist', backref='user', lazy=True)
    viewing_history = db.relationship('ViewingHistory', backref='user', lazy=True)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    genre = db.Column(db.String(50), nullable=False)
    release_year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Float, nullable=False)
    director = db.Column(db.String(50), nullable=False)
    video_url = db.Column(db.String(200), nullable=False)

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movies = db.relationship('Movie', secondary='playlist_movie', backref=db.backref('playlists', lazy='dynamic'))

class PlaylistMovie(db.Model):
    __tablename__ = 'playlist_movie'
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)

class ViewingHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False)
    date_watched = db.Column(db.DateTime, nullable=False)


# Função para verificar se o usuário está autenticado
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']

        if not token:
            return jsonify({'message': 'Token de acesso está faltando!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
            current_user = User.query.filter_by(id=data['user_id']).first()
        except:
            return jsonify({'message': 'Token de acesso é inválido!'}), 401

        return f(current_user, *args, **kwargs)

    return decorated


# Rotas da API

@app.route('/api/filmes/<int:id>/assistir', methods=['POST'])
@token_required  # Requisito: Autenticação de Usuários
def assistir_filme(current_user, id):
    data = request.get_json()
    user_id = current_user.id  # Usuário autenticado
    if not user_id:
        return jsonify({"error": "ID do usuário não fornecido"}), 400

    filme = Movie.query.get(id)
    if not filme:
        return jsonify({"error": "Filme não encontrado"}), 404

    try:
        historico = ViewingHistory(user_id=user_id, movie_id=id)
        db.session.add(historico)
        db.session.commit()
        return jsonify({"message": "Filme assistido registrado com sucesso"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"error": "Erro ao registrar filme assistido"}), 500

@app.route('/api/usuarios/<int:user_id>/historico', methods=['GET'])
@token_required  # Requisito: Autenticação de Usuários
def visualizar_historico(current_user, user_id):
    if current_user.id != user_id:  # Verifica se o usuário autenticado é o mesmo do histórico solicitado
        return jsonify({"error": "Não autorizado"}), 403

    historico = ViewingHistory.query.filter_by(user_id=user_id).all()
    filmes_assistidos = []
    for item in historico:
        filme = Movie.query.get(item.movie_id)
        if filme:
            filmes_assistidos.append({
                "id": filme.id,
                "titulo": filme.title,
                "descricao": filme.description,
                "genero": filme.genre,
                "ano_lancamento": filme.release_year,
                "classificacao": filme.rating,
                "diretor": filme.director
            })
    return jsonify(filmes_assistidos), 200

@app.route('/api/filmes/buscar', methods=['GET'])
def buscar_filmes():
    genero = request.args.get('genero')
    ano = request.args.get('ano')

    filmes_filtrados = Movie.query
    if genero:
        filmes_filtrados = filmes_filtrados.filter_by(genre=genero)
    if ano:
        filmes_filtrados = filmes_filtrados.filter_by(release_year=ano)

    filmes_filtrados = filmes_filtrados.all()

    lista_filmes = []
    for filme in filmes_filtrados:
        dados_filme = {
            "id": filme.id,
            "titulo": filme.title,
            "descricao": filme.description,
            "genero": filme.genre,
            "ano_lancamento": filme.release_year,
            "classificacao": filme.rating,
            "diretor": filme.director
        }
        lista_filmes.append(dados_filme)
    return jsonify(lista_filmes), 200

@app.route('/api/usuarios/<int:user_id>/listas_reproducao', methods=['POST'])
@token_required  # Requisito: Autenticação de Usuários
def criar_lista_reproducao(current_user, user_id):
    if current_user.id != user_id:  # Verifica se o usuário autenticado é o mesmo do histórico solicitado
        return jsonify({"error": "Não autorizado"}), 403

    data = request.get_json()
    nome_lista = data.get('nome_lista')
    filmes = data.get('filmes')

    if not nome_lista:
        return jsonify({"error": "Nome da lista não fornecido"}), 400
    if not filmes:
        return jsonify({"error": "Filmes não fornecidos"}), 400

    lista = Playlist(name=nome_lista, user_id=user_id)
    db.session.add(lista)
    db.session.commit()

    for filme_id in filmes:
        filme = Movie.query.get(filme_id)
        if filme:
            lista.movies.append(filme)

    db.session.commit()
    return jsonify({"message": "Lista de reprodução criada com sucesso"}), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)

