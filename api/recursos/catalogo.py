from flask import Blueprint, jsonify
from sqlalchemy.orm import Session
from infraestrutura.db import SessionLocal
from dominio.servicos import CatalogoServico

bp = Blueprint("catalogo", __name__)

@bp.get("/estados")
def estados():
    with SessionLocal() as s:  # type: Session
        return jsonify(CatalogoServico(s).estados())
