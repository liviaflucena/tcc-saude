import io, os, zipfile
import pandas as pd
import requests
from sqlalchemy import create_engine, text

# CONFIG
DB_URL   = os.getenv("DATABASE_URL", "postgresql+psycopg2://tcc:tcc@db:5432/tcc")
# Recurso público do OpenDataSUS (CSV zipado de Dengue 2025). Se mudar o link, atualize aqui:
DEN_2025 = os.getenv("DENGUE2025_URL",
    "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SINAN/Dengue/csv/DENGBR25.csv.zip"
)

engine = create_engine(DB_URL, future=True)

# Colunas candidatas (variam entre datasets SINAN)
UF_COLS        = ["SG_UF", "SG_UF_NOT", "UF"]
MUN_IBGE_COLS  = ["ID_MUNICIP", "ID_MN_RESI", "CO_MUN_RES", "CO_MUN_NOT", "ID_MUNICIPIO"]
DATE_COLS      = ["DT_NOTIFIC", "DT_SIN_PRI", "DT_NOTIFICACAO", "DT_INVEST", "DT_DIGITA"]

def pick_col(cols, candidates):
    for c in candidates:
        if c in cols: return c
    return None

def to_year_month(series):
    # tenta converter para datetime; aceita múltiplos formatos
    d = pd.to_datetime(series, errors="coerce", dayfirst=True)
    return d.dt.year.astype("Int64"), d.dt.month.astype("Int64")

def ensure_doenca(engine):
    with engine.begin() as con:
        con.execute(text("""
            INSERT INTO doencas(codigo, nome)
            VALUES ('dengue', 'Dengue')
            ON CONFLICT (codigo) DO NOTHING;
        """))
        return con.execute(text("SELECT id FROM doencas WHERE codigo='dengue'")).scalar()

def upsert_casos(engine, df_grp, doenca_id):
    # df_grp: id_ibge, uf, ano, mes, casos
    with engine.begin() as con:
        # garante municípios (esqueleto) — nome/uf podem ser atualizados depois
        ids = df_grp["id_ibge"].dropna().astype(int).unique().tolist()
        if ids:
            con.exec_driver_sql("""
                INSERT INTO municipios (id_ibge, nome, uf, populacao)
                SELECT DISTINCT v::bigint, '', '', 0
                FROM unnest(:ids) AS v
                ON CONFLICT (id_ibge) DO NOTHING;
            """, {"ids": ids})

        # upsert em lotes
        for i in range(0, len(df_grp), 2000):
            ch = df_grp.iloc[i:i+2000].copy()
            ch["doenca_id"] = doenca_id
            con.exec_driver_sql("""
                CREATE TEMP TABLE tmp_casos (
                    id_ibge bigint, uf text, ano int, mes int, casos int, doenca_id int
                ) ON COMMIT DROP;
            """)
            ch[["id_ibge","uf","ano","mes","casos","doenca_id"]].to_sql("tmp_casos", con, if_exists="append", index=False)
            con.exec_driver_sql("""
                INSERT INTO casos (id_ibge, doenca_id, ano, mes, casos, obitos)
                SELECT id_ibge, doenca_id, ano, mes, casos, 0
                FROM tmp_casos
                ON CONFLICT (id_ibge, doenca_id, ano, mes) DO UPDATE SET
                    casos = EXCLUDED.casos;
            """)

def main():
    doenca_id = ensure_doenca(engine)
    print("Baixando Dengue 2025 do OpenDataSUS…")
    r = requests.get(DEN_2025, timeout=180)
    r.raise_for_status()
    zf = zipfile.ZipFile(io.BytesIO(r.content))
    csv_name = next(n for n in zf.namelist() if n.lower().endswith(".csv"))

    # Detecta colunas usando só o header
    with zf.open(csv_name) as f:
        header = pd.read_csv(f, nrows=0, sep=";", dtype=str, encoding="latin1")
    uf_col   = pick_col(header.columns, UF_COLS)
    mun_col  = pick_col(header.columns, MUN_IBGE_COLS)
    date_col = pick_col(header.columns, DATE_COLS)
    if not (uf_col and mun_col and date_col):
        raise RuntimeError(f"Não encontrei colunas esperadas. Header={list(header.columns)}")

    # Lê em chunks para não estourar memória
    aggs = []
    with zf.open(csv_name) as f:
        reader = pd.read_csv(
            f, sep=";", dtype=str, encoding="latin1", chunksize=200_000,
            usecols=[uf_col, mun_col, date_col]
        )
        for idx, chunk in enumerate(reader, 1):
            chunk = chunk.dropna(subset=[mun_col, date_col])
            y, m = to_year_month(chunk[date_col])
            chunk["ano"], chunk["mes"] = y, m
            chunk = chunk.dropna(subset=["ano","mes"])
            chunk["ano"] = chunk["ano"].astype(int)
            chunk["mes"] = chunk["mes"].astype(int)

            # id_ibge como número; remove não numéricos
            chunk["id_ibge"] = chunk[mun_col].str.extract(r"(\d+)", expand=False)
            chunk = chunk.dropna(subset=["id_ibge"])
            chunk["id_ibge"] = chunk["id_ibge"].astype(int)

            chunk["uf"] = chunk[uf_col].str.upper().str.strip()

            grp = (chunk.groupby(["id_ibge","uf","ano","mes"], as_index=False)
                         .size().rename(columns={"size":"casos"}))
            aggs.append(grp)
            print(f"Chunk {idx}: agregados {len(grp)} registros")

    if not aggs:
        print("Nenhum agregado gerado (verifique o dataset).")
        return

    df = pd.concat(aggs, ignore_index=True)
    df = (df.groupby(["id_ibge","uf","ano","mes"], as_index=False)["casos"].sum())

    print(f"Upserting {len(df)} linhas em Postgres…")
    upsert_casos(engine, df, doenca_id)
    print("ETL concluído.")

if __name__ == "__main__":
    main()
