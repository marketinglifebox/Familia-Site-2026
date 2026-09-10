# -*- coding: utf-8 -*-
"""Recorta as fotos dos beneficios.

Doze cartoes de "Beneficios Lifebox" ainda mostram um icone no lugar da foto.
Este script corta cada foto no formato do quadro (342x216, gravado em 2x) e
grava em assets/img/ben-<nome>.jpg. O site troca o icone pela foto sozinho:
beneficios.js so precisa que o arquivo exista.

A entrada pode ser um PDF (uma foto por pagina) ou os proprios arquivos de
imagem, na ordem da lista ORDEM:

    python3 fontes/fotos-beneficios.py fotos.pdf
    python3 fontes/fotos-beneficios.py rosa.jpg trofeu.jpg maos.jpg

Para mandar so algumas, ponha os nomes depois de --nomes, na mesma ordem:

    python3 fontes/fotos-beneficios.py fotos.pdf --nomes cursos odonto
    python3 fontes/fotos-beneficios.py a.jpg b.jpg --nomes funeral premiacoes
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


def do_pdf(caminho):
    """Uma foto por pagina: renderiza cada pagina como imagem."""
    doc = pymupdf.open(caminho)
    larg, alt = QUADRO[0] * ESCALA, QUADRO[1] * ESCALA
    for pagina in doc:
        # renderiza largo o bastante para o recorte nunca ampliar pixel
        zoom = max(larg / pagina.rect.width, alt / pagina.rect.height) * 1.5
        pix = pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom))
        yield Image.frombytes('RGB', (pix.width, pix.height), pix.samples)


def entrada(caminhos):
    for c in caminhos:
        if c.lower().endswith('.pdf'):
            for foto in do_pdf(c):
                yield foto
        else:
            yield Image.open(c).convert('RGB')


def main(caminhos, nomes):
    fotos = list(entrada(caminhos))
    if len(fotos) > len(nomes):
        sys.exit('recebi %d fotos e so %d nomes' % (len(fotos), len(nomes)))

    larg, alt = QUADRO[0] * ESCALA, QUADRO[1] * ESCALA
    for foto, nome in zip(fotos, nomes):
        saida = DESTINO % nome
        recorta(foto, larg, alt).save(saida, quality=88, optimize=True)
        print('gravado', saida, os.path.getsize(saida) // 1024, 'kB')


if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    if '--nomes' in args:
        corte = args.index('--nomes')
        main(args[:corte], args[corte + 1:])
    else:
        main(args, ORDEM)
