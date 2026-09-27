"""
InsurMinds - Projeto Final
Plataforma Inteligente para Análise e Comparação de Apólices D&O

Execução:
    streamlit run app.py
"""

import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from src.comparison_agent import ComparadorApoliceAgent
from src.extraction_agent import ExtratorDocumentoAgent
from src.storage_agent import ArmazenamentoAgent
from src.structuring_agent import EstruturadorApoliceAgent

load_dotenv()

st.set_page_config(page_title="InsurMinds - Projeto Final", page_icon="📑", layout="wide")
st.title("📑 Plataforma Inteligente para Análise e Comparação de Apólices D&O")
st.caption("Projeto Final · InsurMinds · I2A2 — Grupo InsurTech Minds")

armazenamento = ArmazenamentoAgent()

tab_upload, tab_comparar = st.tabs(["1) Upload e Extração", "2) Comparar Apólices"])

# ------------------------------------------------------------------
# ABA 1 — Upload, extração e estruturação
# ------------------------------------------------------------------
with tab_upload:
    st.subheader("Enviar apólice (PDF)")
    arquivo = st.file_uploader("Selecione um arquivo PDF de apólice D&O", type=["pdf"])

    if arquivo is not None and st.button("Processar apólice", type="primary"):
        extrator = ExtratorDocumentoAgent()
        estruturador = EstruturadorApoliceAgent()

        with st.spinner("1) Extraindo texto do documento..."):
            resultado_extracao = extrator.extrair(arquivo.read(), nome_arquivo=arquivo.name)

        st.success(
            f"Texto extraído via **{resultado_extracao['metodo']}** "
            f"({resultado_extracao['num_paginas']} páginas, "
            f"{len(resultado_extracao['texto'])} caracteres)."
        )

        with st.spinner("2) Estruturando informações com IA Generativa..."):
            try:
                dados = estruturador.estruturar(resultado_extracao["texto"])
            except Exception as exc:
                st.error(f"Não foi possível estruturar os dados: {exc}")
                st.stop()

        with st.spinner("3) Salvando no banco de dados..."):
            apolice_id = armazenamento.salvar(
                nome_arquivo=arquivo.name,
                metodo_extracao=resultado_extracao["metodo"],
                dados_estruturados=dados,
                texto_bruto=resultado_extracao["texto"],
            )

        st.success(f"Apólice salva com sucesso (ID {apolice_id}).")
        st.json(dados)

    st.divider()
    st.subheader("Apólices já processadas")
    apolices = armazenamento.listar()
    if not apolices:
        st.info("Nenhuma apólice processada ainda. Envie um PDF acima para começar.")
    else:
        tabela = pd.DataFrame([
            {
                "ID": a["id"],
                "Arquivo": a["nome_arquivo"],
                "Seguradora": a["dados_estruturados"].get("seguradora"),
                "Método extração": a["metodo_extracao"],
                "Processado em": a["criado_em"],
            }
            for a in apolices
        ])
        st.dataframe(tabela, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------
# ABA 2 — Comparação entre apólices
# ------------------------------------------------------------------
with tab_comparar:
    st.subheader("Comparar duas apólices processadas")
    apolices = armazenamento.listar()

    if len(apolices) < 2:
        st.info("Processe pelo menos 2 apólices na aba anterior para poder compará-las.")
    else:
        opcoes = {f"#{a['id']} — {a['nome_arquivo']}": a["id"] for a in apolices}
        col1, col2 = st.columns(2)
        with col1:
            escolha1 = st.selectbox("Apólice 1", list(opcoes.keys()), key="ap1")
        with col2:
            escolha2 = st.selectbox("Apólice 2", list(opcoes.keys()), index=min(1, len(opcoes) - 1), key="ap2")

        if st.button("Comparar", type="primary"):
            if opcoes[escolha1] == opcoes[escolha2]:
                st.warning("Selecione duas apólices diferentes para comparar.")
            else:
                ap1 = armazenamento.obter(opcoes[escolha1])
                ap2 = armazenamento.obter(opcoes[escolha2])
                comparador = ComparadorApoliceAgent()

                st.subheader("Tabela comparativa")
                linhas = comparador.comparar_campos(ap1["dados_estruturados"], ap2["dados_estruturados"])
                df_comp = pd.DataFrame(linhas)[["campo", "apolice_1", "apolice_2", "diferente"]]
                df_comp.columns = ["Campo", ap1["nome_arquivo"], ap2["nome_arquivo"], "Diferente?"]
                st.dataframe(df_comp, use_container_width=True, hide_index=True)

                with st.spinner("Gerando resumo comparativo com IA Generativa..."):
                    resumo = comparador.gerar_resumo_comparativo(
                        ap1["nome_arquivo"], ap1["dados_estruturados"],
                        ap2["nome_arquivo"], ap2["dados_estruturados"],
                    )
                st.subheader("Resumo comparativo (gerado por IA)")
                st.write(resumo)
