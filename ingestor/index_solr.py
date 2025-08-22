import os, json, requests
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://tcc:tcc@db:5432/tcc")
SOLR_URL = os.getenv("SOLR_URL", "http://solr:8983/solr/tcc-saude").rstrip("/")

engine = create_engine(DB_URL, future=True)

SQL = """
SELECT c.id, m.nome AS municipio, m.uf, c.ano, c.mes, c.casos, c.obitos,
       d.codigo AS doenca, d.nome AS doenca_nome
FROM casos c
JOIN municipios m ON m.id_ibge = c.id_ibge
JOIN doencas d   ON d.id = c.doenca_id
"""

def post_batch(docs):
    if not docs:
        return
    resp = requests.post(
        f"{SOLR_URL}/update",
        params={"commitWithin": 1000},  # commit automático até 1s
        headers={"Content-Type": "application/json"},
        data=json.dumps(docs),
        timeout=30,
    )
    resp.raise_for_status()

total = 0
batch = []
BATCH_SIZE = 1000

with engine.begin() as con:
    for row in con.execute(text(SQL)):
        r = dict(row._mapping)
        r["id"] = str(r["id"])  # id deve ser string
        batch.append(r)
        if len(batch) >= BATCH_SIZE:
            post_batch(batch)
            total += len(batch)
            batch.clear()
    if batch:
        post_batch(batch)
        total += len(batch)

# commit final explícito (garante visibilidade imediata)
requests.get(f"{SOLR_URL}/update", params={"commit": "true"}, timeout=10)

print(f"Indexados {total} documentos no Solr em {SOLR_URL}.")
