from typing import List, Dict, Optional
from sqlalchemy import select, func, cast, Float  #  << adicione cast, Float
from sqlalchemy.orm import Session
from dominio.entidades import Doenca, Estado, Municipio, Caso

class RepositorioEstados:
    def __init__(self, s: Session): self.s = s
    def listar(self) -> List[Dict]:
        rows = self.s.execute(select(Estado.codigo_ibge, Estado.uf, Estado.nome)).all()
        return [{"codigo_ibge": a, "uf": b, "nome": c} for a,b,c in rows]

class RepositorioDoencas:
    def __init__(self, s): self.s = s
    def id_por_codigo(self, codigo:str) -> Optional[int]:
        return self.s.execute(select(Doenca.id).where(Doenca.codigo==codigo)).scalar_one_or_none()

class RepositorioIncidencia:
    def __init__(self, s: Session): self.s = s

    def por_uf(self, doenca_id:int, ano:int):
        incid_expr = (
            func.sum(Caso.casos) / func.nullif(func.sum(Municipio.populacao), 0) * 100000.0
        )
        incid = cast(incid_expr, Float).label("incidencia")  # <- força float
        q = (
            select(
                Municipio.uf.label("uf"),
                func.sum(Caso.casos).label("casos"),
                incid,
            )
            .join(Municipio, Municipio.id_ibge == Caso.id_ibge)
            .where(Caso.doenca_id == doenca_id, Caso.ano == ano)
            .group_by(Municipio.uf)
            .order_by(incid.desc())
        )
        return [dict(r._mapping) for r in self.s.execute(q)]

    def por_municipio(self, doenca_id:int, ano:int):
        incid_expr = (
            func.sum(Caso.casos) / func.nullif(func.max(Municipio.populacao), 0) * 100000.0
        )
        incid2 = cast(incid_expr, Float).label("incidencia")  # <- força float
        q = (
            select(
                Municipio.id_ibge,
                Municipio.nome,
                Municipio.uf,
                func.sum(Caso.casos).label("casos"),
                incid2,
            )
            .join(Municipio, Municipio.id_ibge == Caso.id_ibge)
            .where(Caso.doenca_id == doenca_id, Caso.ano == ano)
            .group_by(Municipio.id_ibge, Municipio.nome, Municipio.uf)
            .order_by(incid2.desc())
        )
        return [dict(r._mapping) for r in self.s.execute(q)]

class RepositorioSeries:
    def __init__(self, s: Session): self.s = s
    def mensal(self, doenca_id:int, ano:int, uf:Optional[str]=None):
        q = (
            select(Caso.mes, func.sum(Caso.casos).label("casos"))
            .join(Municipio, Municipio.id_ibge == Caso.id_ibge)
            .where(Caso.doenca_id == doenca_id, Caso.ano == ano)
        )
        if uf:
            q = q.where(Municipio.uf == uf)
        q = q.group_by(Caso.mes).order_by(Caso.mes)
        return [{"mes": m, "casos": c} for m, c in self.s.execute(q)]
