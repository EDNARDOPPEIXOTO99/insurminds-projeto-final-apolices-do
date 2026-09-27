"""
Agente 4 — Comparação entre Apólices.

Recebe os dados estruturados de duas (ou mais) apólices e produz:
1. Uma tabela comparativa campo a campo (determinística, sem LLM).
2. Um resumo em linguagem natural das principais diferenças, gerado por
   IA Generativa, destacando o que mais importa para a tomada de decisão.
"""

import os

CAMPOS_COMPARAVEIS = [
    ("seguradora", "Seguradora"),
    ("limite_maximo_garantia", "Limite Máximo de Garantia"),
    ("franquia", "Franquia"),
    ("ambito_geografico", "Âmbito Geográfico"),
    ("prazo_complementar", "Prazo Complementar"),
]

PROMPT_TEMPLATE = """Você é um especialista em seguros D&O, ajudando um corretor a comparar
duas apólices para orientar um cliente.

Apólice 1 ({nome1}):
{dados1}

Apólice 2 ({nome2}):
{dados2}

Escreva um resumo comparativo objetivo (4 a 8 frases) destacando:
- As diferenças mais relevantes em limites, franquias e âmbito de cobertura.
- Coberturas/extensões presentes em uma apólice e ausentes na outra.
- Exclusões relevantes que diferem entre as duas.
- Uma recomendação neutra do tipo de cliente/perfil de risco para o qual cada apólice seria mais adequada,
  sem afirmar qual é "melhor" de forma absoluta.

Baseie-se exclusivamente nas informações fornecidas acima; não invente dados que não constem nelas.
"""


def _get_llm():
    provider = os.getenv("LLM_PROVIDER", "google").lower()

    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"), temperature=0.2)

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(model=os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6"), temperature=0.2)

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.1"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.2,
        )

    from langchain_google_genai import ChatGoogleGenerativeAI

    return ChatGoogleGenerativeAI(
        model=os.getenv("GOOGLE_MODEL", "gemini-flash-lite-latest"),
        temperature=0.2,
    )


class ComparadorApoliceAgent:
    """Agente responsável por comparar duas apólices estruturadas."""

    def __init__(self):
        self.llm = _get_llm()

    def comparar_campos(self, apolice1: dict, apolice2: dict) -> list[dict]:
        """Comparação determinística campo a campo (sem LLM) — garante que
        a tabela de diferenças seja sempre auditável e reprodutível."""
        linhas = []
        for chave, rotulo in CAMPOS_COMPARAVEIS:
            valor1 = apolice1.get(chave) or "Não informado"
            valor2 = apolice2.get(chave) or "Não informado"
            linhas.append({
                "campo": rotulo,
                "apolice_1": valor1,
                "apolice_2": valor2,
                "diferente": valor1 != valor2,
            })

        linhas.append(self._comparar_listas(
            "Coberturas Básicas", apolice1.get("coberturas_basicas"), apolice2.get("coberturas_basicas")
        ))
        linhas.append(self._comparar_listas(
            "Extensões de Cobertura", apolice1.get("extensoes_de_cobertura"), apolice2.get("extensoes_de_cobertura")
        ))
        linhas.append(self._comparar_listas(
            "Principais Exclusões", apolice1.get("principais_exclusoes"), apolice2.get("principais_exclusoes")
        ))
        return linhas

    def _comparar_listas(self, rotulo: str, lista1, lista2) -> dict:
        lista1 = lista1 or []
        lista2 = lista2 or []
        return {
            "campo": rotulo,
            "apolice_1": "; ".join(lista1) if lista1 else "Não informado",
            "apolice_2": "; ".join(lista2) if lista2 else "Não informado",
            "diferente": set(lista1) != set(lista2),
        }

    def gerar_resumo_comparativo(self, nome1: str, apolice1: dict, nome2: str, apolice2: dict) -> str:
        """Gera, via LLM, um resumo em linguagem natural das diferenças mais
        relevantes entre as duas apólices."""
        prompt = PROMPT_TEMPLATE.format(
            nome1=nome1, dados1=apolice1,
            nome2=nome2, dados2=apolice2,
        )
        response = self.llm.invoke(prompt)
        return _extract_text(response.content)


def _extract_text(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = [b["text"] for b in content if isinstance(b, dict) and b.get("type") == "text"]
        if parts:
            return "\n".join(parts)
    return str(content)
