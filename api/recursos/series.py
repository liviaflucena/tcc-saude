from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from infraestrutura.db import SessionLocal
from dominio.servicos import SeriesServico
from infraestrutura.cache import get_json, set_json

bp = Blueprint("series", __name__)

@bp.get("/series")
def series():
    doenca = request.args.get("disease","dengue")
    ano    = int(request.args.get("year", "2025"))
    uf     = request.args.get("uf")
    key_uf = uf if uf else "ALL"

    cache_key = f"series:{doenca}:{ano}:{key_uf}"
    cached = get_json(cache_key)
    if cached is not None:
        return jsonify({"cache": True, "data": cached})

    with SessionLocal() as s:  # type: Session
        dados = SeriesServico(s).mensal(doenca, ano, uf)
        set_json(cache_key, dados, ttl_seconds=300)
        return jsonify({"cache": False, "data": dados})
