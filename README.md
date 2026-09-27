# InsurMinds — Projeto Final
## Plataforma Inteligente para Análise e Comparação de Apólices D&O

**Grupo InsurTech Minds**

Protótipo (MVP) que automatiza a extração, estruturação e comparação de
apólices de seguro D&O (Directors and Officers), usando OCR, LLMs e
agentes inteligentes — reduzindo um processo que normalmente leva horas
de trabalho manual de especialistas.

## Arquitetura (multiagente)

```
1) ExtratorDocumentoAgent   → extrai texto do PDF (direto ou via OCR se necessário)
2) EstruturadorApoliceAgent → usa LLM para estruturar os dados em JSON padronizado
3) ArmazenamentoAgent       → persiste os dados em banco SQLite
4) ComparadorApoliceAgent   → compara 2 apólices (tabela determinística + resumo por IA)
```

Fluxo: upload do PDF → extração de texto → estruturação via IA → 
armazenamento → seleção de 2 apólices → comparação → apresentação dos
resultados (tabela + resumo em linguagem natural).

## Tecnologias

- Python 3.10+
- Streamlit (interface única, com abas de upload e comparação)
- **pdfplumber** — extração de texto nativo de PDF (usado na maioria dos casos)
- **Tesseract OCR** (via pytesseract + pdf2image) — fallback para apólices
  escaneadas como imagem
- LangChain + **Google Gemini** (gratuito) para estruturação e comparação —
  também suporta Ollama (local/gratuito), Claude e GPT (pagos)
- SQLite (via biblioteca padrão `sqlite3`) — armazenamento estruturado

## Instalação

### 1. Dependências Python
```bash
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Tesseract OCR (necessário apenas para apólices ESCANEADAS)

Se todas as suas apólices de teste forem PDFs de texto nativo (a maioria
das condições gerais publicadas pelas seguradoras é assim), você **pode
pular esta etapa** — o sistema só aciona o OCR quando a extração direta
falha.

**Windows:**
1. Baixe o instalador em https://github.com/UB-Mannheim/tesseract/wiki
2. Instale (padrão: `C:\Program Files\Tesseract-OCR`)
3. Adicione esse caminho à variável de ambiente PATH do Windows
4. Baixe também o Poppler (necessário pelo `pdf2image`): https://github.com/oschwartz10612/poppler-windows/releases — extraia e adicione a pasta `bin` ao PATH

**Linux:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-por poppler-utils
```

## Configuração

```bash
cp .env.example .env
```
Preencha `GOOGLE_API_KEY` (gratuita em https://aistudio.google.com/apikey).
Não é obrigatório pagar por nenhuma API.

## Execução

```bash
streamlit run app.py
```

1. Na aba **"1) Upload e Extração"**, envie um PDF de apólice D&O e clique
   em "Processar apólice". O sistema extrai o texto, estrutura os dados
   via IA e salva no banco local (`apolices.db`).
2. Repita para pelo menos uma segunda apólice.
3. Na aba **"2) Comparar Apólices"**, selecione duas apólices processadas
   e clique em "Comparar" — o sistema mostra uma tabela campo a campo e
   um resumo comparativo gerado por IA.

## Apólices de exemplo para teste

O desafio não disponibiliza apólices reais (documentos sigilosos). Foram
usadas condições gerais D&O públicas, disponibilizadas pelas próprias
seguradoras, para desenvolvimento e testes:

- Berkley: https://www.berkley.com.br/wp-content/uploads/2022/03/CG_DEO.pdf
- Allianz: https://www.allianz.com.br/content/dam/onemarketing/iberolatam/allianz-br/documents/outros-seguros/responsabilidade-civil/directors-e-officers/DG0064_Condi%C3%A7%C3%B5es_Gerais_D-e-O.pdf

Baixe esses PDFs e use-os para testar o upload e a comparação.

## Estrutura do projeto

```
projeto_final/
├── app.py                      # Interface Streamlit (upload + comparação)
├── src/
│   ├── extraction_agent.py     # Agente 1 — extração de texto (PDF/OCR)
│   ├── structuring_agent.py    # Agente 2 — estruturação via LLM
│   ├── storage_agent.py        # Agente 3 — armazenamento SQLite
│   └── comparison_agent.py     # Agente 4 — comparação de apólices
├── data/
│   └── apolices_exemplo/       # (opcional) PDFs de exemplo baixados
├── requirements.txt
├── .env.example
└── README.md
```

## Observações

- O banco de dados (`apolices.db`) é criado automaticamente na primeira
  execução e fica no `.gitignore` (dados de teste não devem ser
  versionados).
- A estruturação via LLM é limitada aos primeiros ~18.000 caracteres do
  documento, o que cobre as cláusulas mais relevantes (objetivo,
  exclusões, franquia) na grande maioria das apólices D&O.
- Chaves de API nunca devem ser commitadas — ficam apenas no `.env`.
- Este é um protótipo (MVP) educacional; não há tratamento de produção,
  autenticação ou criptografia de dados sensíveis.

## Limitações conhecidas e possibilidades de evolução

- A extração via LLM depende da qualidade do texto de entrada; apólices
  com formatação tabular complexa podem exigir ajustes no prompt.
- O prompt de estruturação fornece um modelo literal de JSON (com as
  chaves exatas) para o LLM preencher, e o código ainda normaliza
  pequenas variações de acentuação como rede de segurança — mas modelos
  muito pequenos/gratuitos ocasionalmente podem gerar campos vazios se
  "reinterpretarem" o nome de algum campo; nesse caso, trocar para um
  modelo maior (`gemini-flash-latest` em vez de `gemini-flash-lite-latest`)
  tende a melhorar a aderência ao formato solicitado.
- O OCR (fallback) tem menor precisão que a extração direta, especialmente
  em documentos escaneados de baixa qualidade.
- Evolução natural: suportar mais de 2 apólices na comparação simultânea,
  adicionar exportação do resultado em PDF/Word, e cache de estruturação
  para não reprocessar o mesmo documento.

## Licença

MIT

## Integrantes do grupo — InsurTech Minds

| Nome | Papel |
|---|---|
| Ednardo Pinheiro Peixoto | Representante e Engenheiro de IA/IoT/Tech Líder |
| Glenda dos Santos Tavares | Atuária |
| Sueli Da Hora Moreira | Analytics Engineer |
| Rafael Torres Lattaro Soares | Especialista em Seguros |
