from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    data_criacao = db.Column(db.DateTime, nullable=False)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
class Titulos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(50), nullable=False)
    sinopse = db.Column(db.String(120), nullable=False)
    elenco = db.Column(db.String(120), nullable=False)
    diretor = db.Column(db.String(120), nullable=False)
    ano_lancamento = db.Column(db.String(4), nullable=False)
    ava_media = db.Column(db.Integer, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
class Historico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    id_titulo = db.Column(db.Integer, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
class Lista_reproducao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, nullable=False)
    nome = db.Column(db.String(50), nullable=False)
    descricao = db.Column(db.String(120), nullable=True)
    
    def save(self):
        db.session.add(self)
        db.session.commit()
    
class Lista_reproducao_titulos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_lista = db.Column(db.Integer, nullable=False)
    id_titulo = db.Column(db.Integer, nullable=False)
    
    def save(self):
        db.session.add(self)
        db.session.commit()

class Generos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)

    def save(self):
        db.session.add(self)
        db.session.commit()
