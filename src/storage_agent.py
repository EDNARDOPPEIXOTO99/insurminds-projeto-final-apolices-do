"""
Agente 3 — Armazenamento Estruturado.

Persiste os dados extraídos e estruturados de cada apólice em um banco de
dados SQLite (arquivo local, sem necessidade de servidor de banco de
dados), permitindo consultas e comparações posteriores sem reprocessar
os documentos.
"""

import json
import sqlite3
from datetime import datetime

DB_PATH = "apolices.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS apolices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome_arquivo TEXT NOT NULL,
    metodo_extracao TEXT,
    dados_estruturados TEXT NOT NULL,
    texto_bruto TEXT,
    criado_em TEXT NOT NULL
);
"""


class ArmazenamentoAgent:
    """Agente responsável por salvar e recuperar apólices processadas."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._inicializar_schema()

    def _conectar(self):
        return sqlite3.connect(self.db_path)

    def _inicializar_schema(self):
        with self._conectar() as conn:
            conn.execute(SCHEMA)

    def salvar(self, nome_arquivo: str, metodo_extracao: str, dados_estruturados: dict, texto_bruto: str) -> int:
        with self._conectar() as conn:
            cursor = conn.execute(
                "INSERT INTO apolices (nome_arquivo, metodo_extracao, dados_estruturados, texto_bruto, criado_em) "
                "VALUES (?, ?, ?, ?, ?)",
                (
                    nome_arquivo,
                    metodo_extracao,
                    json.dumps(dados_estruturados, ensure_ascii=False),
                    texto_bruto,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
            return cursor.lastrowid

    def listar(self) -> list[dict]:
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT id, nome_arquivo, metodo_extracao, dados_estruturados, criado_em "
                "FROM apolices ORDER BY id DESC"
            ).fetchall()
        resultado = []
        for row in rows:
            item = dict(row)
            item["dados_estruturados"] = json.loads(item["dados_estruturados"])
            resultado.append(item)
        return resultado

    def obter(self, apolice_id: int) -> dict | None:
        with self._conectar() as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM apolices WHERE id = ?", (apolice_id,)).fetchone()
        if row is None:
            return None
        item = dict(row)
        item["dados_estruturados"] = json.loads(item["dados_estruturados"])
        return item
