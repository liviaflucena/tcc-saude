# api/dominio/servicos.py
from typing import Optional, List, Dict   # <-- ADICIONE isto

from sqlalchemy.orm import Session
from infraestrutura.repositorios import (
    RepositorioEstados, RepositorioDoencas, RepositorioIncidencia, RepositorioSeries
)

class CatalogoServico:
    def __init__(self, s: Session): self.rep_e = RepositorioEstados(s)
    def estados(self): return self.rep_e.listar()

class IncidenciaServico:
    def __init__(self, s):
        self.rep_d = RepositorioDoencas(s)
        self.rep_i = RepositorioIncidencia(s)
    def agrupar(self, doenca:str, ano:int, agg:str="uf"):
        did = self.rep_d.id_por_codigo(doenca)
        if did is None:
            return []  # doença não cadastrada -> sem dados (evita 500)
        return self.rep_i.por_uf(did, ano) if agg == "uf" else self.rep_i.por_municipio(did, ano)

class SeriesServico:
    def __init__(self, s):
        self.rep_d = RepositorioDoencas(s)
        self.rep_s = RepositorioSeries(s)
    def mensal(self, doenca:str, ano:int, uf:Optional[str]=None):
        did = self.rep_d.id_por_codigo(doenca)
        if did is None:
            return []
        return self.rep_s.mensal(did, ano, uf)

