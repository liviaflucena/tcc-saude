# api/recursos/saude.py
from flask import Blueprint, jsonify
from infraestrutura.db import ping_db
from infraestrutura.cache import ping as cache_ping
import os, requests

bp = Blueprint("saude", __name__)

def ping_solr():
    url = os.getenv("SOLR_URL", "http://solr:8983/solr/tcc-saude").rstrip("/") + "/admin/ping"
    try:
        r = requests.get(url, timeout=3)
        return r.status_code == 200
    except Exception:
        return False

@bp.get("/health")
def health():
    return jsonify({"ok": True, "db": ping_db(), "cache": cache_ping(), "search": ping_solr()})
