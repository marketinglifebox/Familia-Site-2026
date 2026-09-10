# -*- coding: utf-8 -*-
"""Recorta as fotos dos beneficios a partir de um PDF.

Doze cartoes de "Beneficios Lifebox" ainda mostram um icone no lugar da foto.
Assim que as fotos chegarem num PDF - uma por pagina, na ordem da lista abaixo
-, este script corta cada uma no formato do quadro (342x216, gravado em 2x) e
grava em assets/img/ben-<nome>.jpg. O site troca o icone pela foto sozinho:
beneficios.js so precisa que o arquivo exista.

    python3 fontes/fotos-beneficios.py caminho/do/arquivo.pdf

Para mandar so algumas fotos, passe os nomes na ordem das paginas:

    python3 fontes/fotos-beneficios.py fotos.pdf cursos odonto transporte
"""
import os
import sys

import pymupdf
from PIL import Image

# a ordem dos cartoes sem foto no carrossel, de cima a baixo do index.html
ORDEM = ['totalpass', 'cursos', 'funeral', 'odonto', 'freela', 'assiduidade',
         'saude', 'premiacoes', 'transporte', 'seguro', 'natalidade', 'agenda']

QUADRO = (342, 216)          # a medida de .benef-foto
ESCALA = 2                   # grava em dobro, para telas densas
DESTINO = 'assets/img/ben-%s.jpg'


def recorta(imagem, larg, alt):
    """Enquadra no centro, do jeito que o CSS faria com object-fit:cover."""
    escala = max(larg / imagem.width, alt / imagem.height)
    nova = imagem.resize((max(larg, round(imagem.width * escala)),
                          max(alt, round(imagem.height * escala))),
                         Image.LANCZOS)
    esq = (nova.width - larg) // 2
    topo = (nova.height - alt) // 2
    return nova.crop((esq, topo, esq + larg, topo + alt))


def main(pdf, nomes):
    doc = pymupdf.open(pdf)
    if len(nomes) < len(doc):
        sys.exit('o PDF tem %d paginas e so recebi %d nomes' % (len(doc), len(nomes)))

    larg, alt = QUADRO[0] * ESCALA, QUADRO[1] * ESCALA
    for i, pagina in enumerate(doc):
        # renderiza largo o bastante para o recorte nunca ampliar pixel
        zoom = max(larg / pagina.rect.width, alt / pagina.rect.height) * 1.5
        pix = pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        foto = Image.frombytes('RGB', (pix.width, pix.height), pix.samples)
        saida = DESTINO % nomes[i]
        recorta(foto, larg, alt).save(saida, quality=88, optimize=True)
        print('gravado', saida, os.path.getsize(saida) // 1024, 'kB')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2:] or ORDEM)
