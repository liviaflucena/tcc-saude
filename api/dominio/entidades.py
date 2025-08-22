from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import CHAR

class Base(DeclarativeBase): pass

class Doenca(Base):
    __tablename__ = "doencas"
    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    nome:   Mapped[str] = mapped_column(String, nullable=False)

class Estado(Base):
    __tablename__ = "estados"
    codigo_ibge: Mapped[int] = mapped_column(Integer, primary_key=True)
    uf:          Mapped[str] = mapped_column(CHAR(2), unique=True, nullable=False)
    nome:        Mapped[str] = mapped_column(String, nullable=False)
    populacao:   Mapped[int] = mapped_column(Integer, nullable=True)

class Municipio(Base):
    __tablename__ = "municipios"
    id_ibge:   Mapped[str] = mapped_column(CHAR(7), primary_key=True)
    nome:      Mapped[str] = mapped_column(String, nullable=False)
    uf:        Mapped[str] = mapped_column(CHAR(2), ForeignKey("estados.uf"), nullable=False)
    populacao: Mapped[int] = mapped_column(Integer, nullable=True)

class Caso(Base):
    __tablename__ = "casos"
    id:        Mapped[int] = mapped_column(primary_key=True)
    doenca_id: Mapped[int] = mapped_column(ForeignKey("doencas.id"))
    id_ibge:   Mapped[str] = mapped_column(CHAR(7), ForeignKey("municipios.id_ibge"))
    ano:       Mapped[int] = mapped_column(Integer)
    mes:       Mapped[int] = mapped_column(Integer, nullable=True)
    casos:     Mapped[int] = mapped_column(Integer, default=0)
    obitos:    Mapped[int] = mapped_column(Integer, default=0)
