"""
Agente 2 — Estruturação de Informações via IA Generativa.

Recebe o texto bruto extraído da apólice (Agente 1) e usa um LLM para
identificar e estruturar as informações relevantes em um formato
padronizado (JSON), cobrindo os elementos que mais importam para
comparação de apólices D&O: seguradora, limites, franquias, coberturas,
exclusões e extensões.
"""

import json
import os
import re

CAMPOS_ESPERADOS = [
    "seguradora", "tomador", "vigencia_inicio", "vigencia_fim",
    "limite_maximo_garantia", "franquia", "coberturas_basicas",
    "extensoes_de_cobertura", "principais_exclusoes", "ambito_geografico",
    "prazo_complementar",
]

# IMPORTANTE: o modelo já se mostrou capaz de "traduzir" ou renomear as
# chaves do JSON por conta própria (ex.: "seguradora" -> "proteção",
# "tomador" -> "bebedor") quando o prompt só descrevia os campos em
# prosa. Por isso o prompt abaixo fornece um MODELO LITERAL de JSON a
# ser copiado e preenchido, reforçando por duas vezes que as chaves não
# devem ser alteradas.
PROMPT_TEMPLATE = """Você é um especialista em análise de apólices de seguro D&O
(Directors and Officers / Responsabilidade Civil de Administradores).

Leia o texto abaixo, extraído de uma apólice ou de suas condições gerais, e
preencha o JSON no formato EXATO abaixo, com ESTAS MESMAS CHAVES, sem
traduzir, renomear, adicionar acentos diferentes ou criar chaves novas.
Copie os nomes das chaves exatamente como estão no modelo. Se uma
informação não estiver disponível no texto, mantenha o valor null. Não
invente valores.

MODELO EXATO A PREENCHER (copie as chaves, substitua apenas os valores):
{{
  "seguradora": null,
  "tomador": null,
  "vigencia_inicio": null,
  "vigencia_fim": null,
  "limite_maximo_garantia": null,
  "franquia": null,
  "coberturas_basicas": [],
  "extensoes_de_cobertura": [],
  "principais_exclusoes": [],
  "ambito_geografico": null,
  "prazo_complementar": null
}}

Significado de cada chave (não altere os nomes das chaves ao responder):
- "seguradora": nome da seguradora
- "tomador": nome do tomador do seguro (se disponível; caso contrário null)
- "vigencia_inicio": data de início de vigência (se disponível; senão null)
- "vigencia_fim": data de término de vigência (se disponível; senão null)
- "limite_maximo_garantia": valor do Limite Máximo de Garantia (LMG), como string
- "franquia": valor(es) de franquia aplicável, como string
- "coberturas_basicas": lista de strings com as coberturas básicas identificadas
- "extensoes_de_cobertura": lista de strings com as principais extensões de cobertura mencionadas
- "principais_exclusoes": lista de strings com as principais exclusões de risco (até 10 mais relevantes)
- "ambito_geografico": descrição do âmbito geográfico da cobertura
- "prazo_complementar": duração do prazo complementar/adicional, se mencionado

Responda APENAS com o JSON preenchido, usando exatamente as chaves do
modelo acima (não traduza nem renomeie nenhuma chave), sem nenhum texto
adicional antes ou depois.

TEXTO DA APÓLICE:
{texto}
"""


def _get_llm():
    provider = os.getenv("LLM_PROVIDER", "google").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"), temperature=0)

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-flash-lite-latest"),
        temperature=0,
    )


class EstruturadorApoliceAgent:
    """Agente responsável por transformar texto bruto em dados estruturados,
    usando um LLM para interpretar a linguagem jurídica da apólice."""

    def __init__(self):
        self.llm = _get_llm()

    def estruturar(self, texto: str) -> dict:
        # Textos de apólices são longos; usamos um recorte representativo
        # (início + eventuais seções de exclusões/coberturas) para caber
        # no contexto do modelo sem perder as partes mais relevantes.
        texto_recortado = texto[:200000]

        prompt = PROMPT_TEMPLATE.format(texto=texto_recortado)
        response = self.llm.invoke(prompt)
        conteudo = _extract_text(response.content)
        dados = self._parse_json_seguro(conteudo)
        return self._normalizar_chaves(dados)

    def _parse_json_seguro(self, conteudo: str) -> dict:
        """Extrai o JSON da resposta do LLM de forma tolerante a pequenas
        variações de formatação (ex.: blocos ```json ... ```)."""
        limpo = re.sub(r"^```(?:json)?|```$", "", conteudo.strip(), flags=re.MULTILINE).strip()
        try:
            dados = json.loads(limpo)
        except json.JSONDecodeError:
            # último recurso: tenta achar o primeiro '{' e o último '}'
            inicio, fim = limpo.find("{"), limpo.rfind("}")
            if inicio != -1 and fim != -1:
                dados = json.loads(limpo[inicio:fim + 1])
            else:
                raise ValueError(f"Não foi possível interpretar a resposta do LLM como JSON: {conteudo[:300]}")
        return dados

    def _normalizar_chaves(self, dados: dict) -> dict:
        """Rede de segurança: se o LLM, mesmo assim, retornar alguma chave
        com grafia ligeiramente diferente (ex.: com/sem acento), tenta
        casar por normalização antes de aplicar o valor padrão None."""
        normalizado = {}
        chaves_originais = {self._normalizar_string(k): k for k in dados.keys()}

        for campo in CAMPOS_ESPERADOS:
            chave_normalizada = self._normalizar_string(campo)
            if chave_normalizada in chaves_originais:
                normalizado[campo] = dados[chaves_originais[chave_normalizada]]
            else:
                normalizado[campo] = None
        return normalizado

    @staticmethod
    def _normalizar_string(s: str) -> str:
        import unicodedata
        s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode("ascii")
        return s.lower().strip()


def _extract_text(content) -> str:
    """Normaliza a saída do LLM para string (Gemini pode retornar lista de blocos)."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b["text"] for b in content if isinstance(b, dict) and b.get("type") == "text"]
        if parts:
            return "\n".join(parts)
    return str(content)
