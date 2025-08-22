from flask import Blueprint, request, jsonify
from sqlalchemy.orm import Session
from infraestrutura.db import SessionLocal
from dominio.servicos import IncidenciaServico
from infraestrutura.cache import get_json, set_json

bp = Blueprint("incidencia", __name__)

@bp.get("/incidence")
def incidence():
    doenca = request.args.get("disease","dengue")
    ano    = int(request.args.get("year", "2025"))
    agg    = request.args.get("agg","uf")  # uf|municipio

    cache_key = f"inc:{doenca}:{ano}:{agg}"
    cached = get_json(cache_key)
    if cached is not None:
        return jsonify({"cache": True, "data": cached})

    with SessionLocal() as s:  # type: Session
        dados = IncidenciaServico(s).agrupar(doenca, ano, agg)
        set_json(cache_key, dados, ttl_seconds=300)  # 5 min
        return jsonify({"cache": False, "data": dados})
