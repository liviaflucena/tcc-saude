import os
from flask import Flask
from flask_cors import CORS
from flask_restful import Api
from recursos.saude import bp as saude_bp
from recursos.catalogo import bp as catalogo_bp
from recursos.incidencia import bp as incidencia_bp
from recursos.series import bp as series_bp
from infraestrutura.db import criar_tabelas
from infraestrutura.seed_estados import seed as seed_estados
from recursos.busca import bp as busca_bp

def create_app():
    app = Flask(__name__)
    CORS(app, origins=os.getenv("CORS_ORIGINS", "*"))
    Api(app)
    criar_tabelas()
    seed_estados()
    app.register_blueprint(saude_bp, url_prefix="/api")
    app.register_blueprint(catalogo_bp, url_prefix="/api")
    app.register_blueprint(incidencia_bp, url_prefix="/api")
    app.register_blueprint(series_bp, url_prefix="/api")
    app.register_blueprint(busca_bp, url_prefix="/api")
    return app
