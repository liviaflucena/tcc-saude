from sqlalchemy import text
from infraestrutura.db import engine

ESTADOS = [
 (11,'RO','Rondônia'),(12,'AC','Acre'),(13,'AM','Amazonas'),(14,'RR','Roraima'),
 (15,'PA','Pará'),(16,'AP','Amapá'),(17,'TO','Tocantins'),(21,'MA','Maranhão'),
 (22,'PI','Piauí'),(23,'CE','Ceará'),(24,'RN','Rio Grande do Norte'),(25,'PB','Paraíba'),
 (26,'PE','Pernambuco'),(27,'AL','Alagoas'),(28,'SE','Sergipe'),(29,'BA','Bahia'),
 (31,'MG','Minas Gerais'),(32,'ES','Espírito Santo'),(33,'RJ','Rio de Janeiro'),(35,'SP','São Paulo'),
 (41,'PR','Paraná'),(42,'SC','Santa Catarina'),(43,'RS','Rio Grande do Sul'),
 (50,'MS','Mato Grosso do Sul'),(51,'MT','Mato Grosso'),(52,'GO','Goiás'),(53,'DF','Distrito Federal')
]

def seed():
    with engine.begin() as con:
        con.execute(text("""
           CREATE TABLE IF NOT EXISTS estados (
             codigo_ibge INT PRIMARY KEY,
             uf CHAR(2) UNIQUE NOT NULL,
             nome TEXT NOT NULL,
             populacao INT
           )
        """))
        for cod, uf, nome in ESTADOS:
            con.execute(text("""
               INSERT INTO estados(codigo_ibge, uf, nome)
               VALUES (:cod, :uf, :nome)
               ON CONFLICT (codigo_ibge) DO NOTHING
            """), {"cod": cod, "uf": uf, "nome": nome})
