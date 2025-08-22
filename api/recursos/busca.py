import os
import requests
from flask import Blueprint, request, jsonify
from urllib.parse import quote

bp = Blueprint("busca", __name__)
SOLR_URL = os.getenv("SOLR_URL", "http://solr:8983/solr/tcc-saude").rstrip("/")

def fq_field(name: str, value) -> str:
    return f'{name}:{quote(str(value))}'

@bp.get("/search")
def search():
    # Suporta: q=...  OU  doenca=&uf=&municipio=&ano=&mes=
    q_raw   = (request.args.get("q") or "").strip()
    doenca  = request.args.get("doenca")
    uf      = request.args.get("uf")
    municipio = request.args.get("municipio")
    ano     = request.args.get("ano")
    mes     = request.args.get("mes")
    rows    = int(request.args.get("rows") or "20")

    params = {"wt": "json", "rows": rows}
    if q_raw:
        params["q"] = q_raw
    else:
        params["q"] = "*:*"
        fqs = []
        if doenca:   fqs.append(fq_field("doenca", doenca))
        if uf:       fqs.append(fq_field("uf", uf))
        if municipio:fqs.append(fq_field("municipio", municipio))
        if ano:      fqs.append(fq_field("ano", ano))
        if mes:      fqs.append(fq_field("mes", mes))
        if fqs:
            params["fq"] = fqs

    try:
        r = requests.get(f"{SOLR_URL}/select", params=params, timeout=10)
        if r.status_code != 200:
            return jsonify({
                "error": "solr_bad_status",
                "status": r.status_code,
                "url": r.url,
                "text": r.text[:500],
            }), 502

        js = r.json()
        docs = js.get("response", {}).get("docs", [])
        return jsonify({"data": docs}), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": "solr_request_failed", "detail": str(e)}), 502
    except ValueError as e:
        return jsonify({"error": "solr_invalid_json", "detail": str(e)}), 502
