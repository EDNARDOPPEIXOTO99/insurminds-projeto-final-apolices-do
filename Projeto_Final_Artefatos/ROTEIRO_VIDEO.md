# Roteiro do vídeo — InsurMinds_Projeto_Final.mp4

**Duração alvo: até 5 minutos.** Grave a tela (Streamlit rodando) com narração ao
vivo ou dublada depois. Sugestão de ferramenta gratuita: OBS Studio, ou a própria
gravação de tela do Windows (Win+Alt+R já grava a janela ativa com áudio).

---

## 1) Abertura (0:00 – 0:30) — ~30s

*Mostre o slide 1 do Pitch Deck (capa) ou a tela inicial do app.*

> "Olá! Somos o grupo InsurTech Minds, e este é o nosso Projeto Final do curso
> InsurMinds, da I2A2: uma Plataforma Inteligente para Análise e Comparação de
> Apólices D&O — seguros de Responsabilidade Civil de Administradores."

## 2) O problema (0:30 – 1:10) — ~40s

*Mostre o slide 2 do Pitch Deck (O problema).*

> "Apólices D&O são documentos longos, escritos em linguagem jurídica densa —
> muitas vezes com mais de 60 páginas. Comparar duas apólices manualmente, campo
> a campo, para identificar diferenças em coberturas, exclusões e limites, pode
> levar várias horas de trabalho de um especialista. Foi esse problema que
> decidimos resolver."

## 3) A solução e a arquitetura (1:10 – 2:00) — ~50s

*Mostre os slides 3 e 4 do Pitch Deck (A solução / Arquitetura multiagente).*

> "Nossa solução usa OCR e Inteligência Artificial Generativa para automatizar
> esse processo, através de 4 agentes especializados: o primeiro extrai o texto
> do PDF; o segundo usa o Google Gemini para estruturar as informações em um
> formato padronizado; o terceiro armazena esses dados; e o quarto compara duas
> apólices, gerando tanto uma tabela objetiva quanto um resumo em linguagem
> natural."

## 4) Demonstração ao vivo (2:00 – 4:00) — ~2min

*Aqui é a parte mais importante: grave a tela do navegador com o Streamlit rodando.*

1. Mostre a aba **"1) Upload e Extração"**.
2. Envie o PDF da apólice Allianz. Comente em voz alta:
   > "Vou enviar aqui a primeira apólice — condições gerais da Allianz, um
   > documento público de mais de 50 páginas."
3. Clique em "Processar apólice" e espere aparecer o JSON estruturado. Comente:
   > "Em poucos segundos, o sistema extraiu o texto e já estruturou os dados —
   > seguradora, âmbito geográfico, prazo complementar, coberturas e exclusões."
4. Repita rapidamente com a segunda apólice (Berkley) — pode acelerar/cortar essa
   parte se quiser economizar tempo.
5. Vá para a aba **"2) Comparar Apólices"**, selecione as duas, clique em
   "Comparar". Comente:
   > "Agora, com as duas apólices já processadas, pedimos a comparação. O
   > sistema gera uma tabela objetiva, campo a campo, e também um resumo
   > comparativo em linguagem natural, escrito por IA, que já aponta o perfil de
   > risco mais adequado para cada apólice."
6. Deixe a câmera/tela alguns segundos no resumo gerado pela IA, lendo um trecho
   em voz alta.

## 5) Resultados e encerramento (4:00 – 4:45) — ~45s

*Mostre os slides 6, 7 e 8 do Pitch Deck (Resultado real / Limitações / Obrigado).*

> "Testamos com duas apólices reais e públicas — Allianz e Berkley — e o sistema
> identificou corretamente diferenças relevantes, como o âmbito geográfico e o
> prazo complementar de cada uma. Sabemos das limitações: por exemplo, valores
> específicos de franquia e limite de garantia costumam estar em um documento
> separado, a Especificação da Apólice, que não estava disponível nos exemplos
> públicos que usamos — e, nesses casos, o sistema é honesto e reporta
> 'não informado', em vez de inventar um número.
>
> Como próximos passos, gostaríamos de suportar a comparação de mais de duas
> apólices ao mesmo tempo e exportar o resultado em PDF.
>
> Obrigado pela atenção! Esse foi o projeto final do grupo InsurTech Minds."

---

## Checklist antes de gravar

- [ ] `.env` configurado com chave de API válida (Google Gemini)
- [ ] `streamlit run app.py` já rodando, sem erros no terminal
- [ ] Banco `apolices.db` limpo (ou já com as 2 apólices de teste processadas,
      se preferir pular a etapa de upload ao vivo para ganhar tempo)
- [ ] Navegador em tela cheia, sem abas/favoritos visíveis desnecessários
- [ ] Testar o áudio antes de gravar a versão final

## Depois de gravar

1. Salve o arquivo com o nome exato **`InsurMinds_Projeto_Final.mp4`**
2. Coloque-o na pasta `Projeto_Final_Artefatos/` do repositório GitHub, junto
   com o Pitch Deck (`InsurMinds_Projeto_Final.pptx`)
