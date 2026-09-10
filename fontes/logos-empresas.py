# -*- coding: utf-8 -*-
"""Recorta os logos das empresas do grupo a partir dos PDFs entregues.

Cada PDF traz um logo numa prancheta com muita margem em volta. Aqui a pagina
e rasterizada com canal alfa - o traco e branco e precisa continuar vazado
sobre o laranja da faixa -, recortada no exato retangulo que tem tinta e
gravada em assets/img/empresas/<nome>.png.

O recorte na tinta e o que importa: com a margem da prancheta, o object-fit
:contain encolheria o logo para caber a folga junto, e ele apareceria bem
menor do que o espaco de 208x84 reservado no documento.

    python3 fontes/logos-empresas.py <pasta com os PDFs>
"""
import os
import sys

import pymupdf
from PIL import Image

# o que cada prancheta traz, conferido a olho no render
MAPA = {
    'Prancheta 2': 'car-boss',       # CAR.BOSS
    'Prancheta 3': 'dog-days',       # DOG DAYS HOTDOG
    'Prancheta 4': 'vuca-solution',  # VUCA FOOD
    'Prancheta 5': 'burger-cheff',   # Burger CHEFF
}

LADO_MAIOR = 800          # resolucao de gravacao; o quadro no site tem 208x84
DESTINO = 'assets/img/empresas/%s.png'


def recorta(pdf):
    """Rasteriza a primeira pagina com alfa e devolve so o retangulo com tinta."""
    pagina = pymupdf.open(pdf)[0]
    zoom = 2000 / pagina.rect.width
    pix = pagina.get_pixmap(matrix=pymupdf.Matrix(zoom, zoom), alpha=True)
    im = Image.frombytes('RGBA', (pix.width, pix.height), pix.samples)
    caixa = im.split()[3].getbbox()      # onde o alfa nao e zero
    if not caixa:
        sys.exit('%s: pagina sem tinta' % pdf)
    return im.crop(caixa)


def main(pasta):
    os.makedirs('assets/img/empresas', exist_ok=True)
    for prancheta, nome in sorted(MAPA.items()):
        pdf = os.path.join(pasta, prancheta + '.pdf')
        if not os.path.exists(pdf):
            print('faltando:', pdf)
            continue
        im = recorta(pdf)
        escala = LADO_MAIOR / max(im.width, im.height)
        if escala < 1:
            im = im.resize((round(im.width * escala), round(im.height * escala)),
                           Image.LANCZOS)
        saida = DESTINO % nome
        im.save(saida, optimize=True)
        print('%-14s -> %-38s %dx%d  %d kB' %
              (prancheta, saida, im.width, im.height, os.path.getsize(saida) // 1024))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1])
