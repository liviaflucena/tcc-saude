import os
import pandas as pd
from sqlalchemy import create_engine, text

DB_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://tcc:tcc@db:5432/tcc")
engine = create_engine(DB_URL, future=True)

csv_path = "/app/data/exemplo_dengue.csv"
df = pd.read_csv(csv_path, dtype={"id_ibge": str, "uf": str})
df["id_ibge"] = df["id_ibge"].str.zfill(7)

with engine.begin() as con:
    con.exec_driver_sql("""
        CREATE TABLE IF NOT EXISTS doencas (
          id SERIAL PRIMARY KEY,
          codigo TEXT UNIQUE NOT NULL,
          nome   TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS municipios (
          id_ibge CHAR(7) PRIMARY KEY,
          nome TEXT NOT NULL,
          uf CHAR(2) NOT NULL,
          populacao INT
        );
        CREATE TABLE IF NOT EXISTS casos (
          id SERIAL PRIMARY KEY,
          doenca_id INT NOT NULL,
          id_ibge CHAR(7) NOT NULL,
          ano INT NOT NULL,
          mes INT,
          casos INT DEFAULT 0,
          obitos INT DEFAULT 0
        );
    """)
    con.execute(text("""
        INSERT INTO doencas (codigo, nome)
        VALUES ('dengue','Dengue')
        ON CONFLICT (codigo) DO NOTHING;
    """))

df.to_sql("staging_casos", engine, if_exists="replace", index=False)

with engine.begin() as con:
    con.exec_driver_sql("""
        INSERT INTO municipios (id_ibge, nome, uf, populacao)
        SELECT DISTINCT
            id_ibge,
            name AS nome,
            uf,
            population AS populacao
        FROM staging_casos
        ON CONFLICT (id_ibge) DO UPDATE SET
          nome      = EXCLUDED.nome,
          uf        = EXCLUDED.uf,
          populacao = EXCLUDED.populacao;
    """)
    con.exec_driver_sql("""
        INSERT INTO casos (doenca_id, id_ibge, ano, mes, casos, obitos)
        SELECT (SELECT id FROM doencas WHERE codigo='dengue'),
               id_ibge, year, month, cases, COALESCE(deaths,0)
        FROM staging_casos;
    """)
print("ETL semente concluído.")
