"""
Agente 1 — Recepção e Extração de Documentos.

Recebe um arquivo PDF (apólice de seguro D&O) e extrai o texto bruto.

Estratégia em duas camadas:
1. Extração direta de texto (pdfplumber) — funciona para a grande maioria
   das apólices, que são PDFs de texto nativo (gerados digitalmente pelas
   seguradoras).
2. OCR via Tesseract (pytesseract + pdf2image), usado como FALLBACK apenas
   quando a extração direta não retorna texto suficiente — ou seja, quando
   o PDF é uma imagem escaneada.

Essa abordagem evita o custo computacional do OCR quando não é necessário,
mas garante que documentos escaneados também sejam suportados, conforme
exigido pelo edital ("permitir a leitura de documentos em PDF ou imagem").
"""

import io

import pdfplumber

MIN_CHARS_FOR_VALID_TEXT = 200  # abaixo disso, consideramos que precisa de OCR


class ExtratorDocumentoAgent:
    """Agente responsável por extrair texto bruto de um PDF de apólice."""

    def extrair(self, file_bytes: bytes, nome_arquivo: str = "") -> dict:
        """Retorna um dicionário com o texto extraído e metadados sobre o
        método de extração usado."""
        texto_direto = self._extrair_texto_direto(file_bytes)

        if len(texto_direto.strip()) >= MIN_CHARS_FOR_VALID_TEXT:
            return {
                "nome_arquivo": nome_arquivo,
                "texto": texto_direto,
                "metodo": "extracao_direta",
                "num_paginas": self._contar_paginas(file_bytes),
            }

        # Fallback: OCR (só é executado se a extração direta falhar/for insuficiente)
        texto_ocr = self._extrair_via_ocr(file_bytes)
        return {
            "nome_arquivo": nome_arquivo,
            "texto": texto_ocr,
            "metodo": "ocr_tesseract",
            "num_paginas": self._contar_paginas(file_bytes),
        }

    def _extrair_texto_direto(self, file_bytes: bytes) -> str:
        partes = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                texto_pagina = page.extract_text() or ""
                partes.append(texto_pagina)
        return "\n".join(partes)

    def _contar_paginas(self, file_bytes: bytes) -> int:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            return len(pdf.pages)

    def _extrair_via_ocr(self, file_bytes: bytes) -> str:
        """OCR usado apenas quando o PDF não tem texto extraível
        diretamente (ex.: apólice escaneada como imagem)."""
        try:
            import pytesseract
            from pdf2image import convert_from_bytes
        except ImportError as exc:
            raise RuntimeError(
                "OCR necessário, mas as dependências (pytesseract, pdf2image, "
                "poppler) não estão instaladas. Veja o README para instruções."
            ) from exc

        imagens = convert_from_bytes(file_bytes, dpi=200)
        partes = []
        for imagem in imagens:
            texto = pytesseract.image_to_string(imagem, lang="por")
            partes.append(texto)
        return "\n".join(partes)
