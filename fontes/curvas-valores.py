# -*- coding: utf-8 -*-
"""Fundo verde da pagina "Valores".

O PDF veio achatado: onde os titulos e os paragrafos passavam por cima das
curvas, o traco ficou com o desenho das letras recortado dentro dele. As
fotos e os cartoes tambem tapam trechos, mas esses continuam tapados na
pagina - ja os textos nao, porque a fonte que uso nao e a mesma do documento
e o buraco nao coincidiria com as letras, deixando um halo verde-vazado em
volta de cada palavra.

Entao: fecha-se a mancha verde apenas onde havia tinta de texto (fechamento
morfologico limitado a essa area, que atravessa tracos finos e nao mexe nas
oclusoes grandes) e vetoriza-se o resultado.
"""
import re, subprocess
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage

SP  = '/tmp/claude-0/-home-user-Familia-Site-2026/f5a484da-fb78-5b61-8d16-a736d78a1c8f/scratchpad/'
DEST = '/home/user/Familia-Site-2026/assets/svg/curves-valores.svg'
TOPO = 106                      # abaixo do cabecalho azul

# retangulos que continuam tapados na pagina (fotos e a faixa de cartoes)
TAPADOS = [(284, 630, 1271, 1123), (279, 1452, 1266, 1944),
           (-364, 2362, 365, 2620), (416, 2362, 1145, 2620), (1196, 2362, 1925, 2620)]

A = np.asarray(Image.open(SP + 'page3.png').convert('RGB')).astype(int)
H, W = A.shape[:2]
# so a distancia ate o verde nao basta: um pixel cinza de antialias de texto
# tambem cai perto dele. Exige-se tambem que o verde domine o vermelho e o azul
verde = ((np.abs(A - np.array([100, 165, 104])).sum(2) < 90) &
         (A[:, :, 1] - (A[:, :, 0] + A[:, :, 2]) / 2 > 15))
creme = np.abs(A - np.array([253, 246, 239])).sum(2) < 40
verde[:TOPO] = False

# "tinta de texto" pelas duas cores que ela tem no documento - preto e
# laranja. Definir por exclusao (nem creme nem verde) pegaria tambem a franja
# de antialias das proprias curvas, e o fechamento engordaria todos os tracos
texto = ((A.max(2) < 130) |
         (np.abs(A - np.array([232, 101, 50])).sum(2) < 110))
texto[:TOPO] = False
for x0, y0, x1, y1 in TAPADOS:
    texto[y0:y1 + 1, x0:x1 + 1] = False
texto = ndimage.binary_dilation(texto, np.ones((13, 13)))

r = 22
disco = np.hypot(*np.ogrid[-r:r + 1, -r:r + 1]) <= r
fechado = ndimage.binary_closing(verde, disco)
cheio = verde | (fechado & texto)
cheio = ndimage.binary_fill_holes(cheio)      # buracos fechados por dentro

# migalhas: onde uma letra pegava so a beirada de uma curva sobram farpas de
# poucos pixels. Fica so o que tem um miolo de traco de verdade
nucleo = ndimage.binary_erosion(cheio, np.ones((7, 7)))
lb, nn = ndimage.label(nucleo, structure=np.ones((3, 3)))
bom = np.zeros(nn + 1, bool)
bom[1:] = np.array(ndimage.sum(nucleo, lb, range(1, nn + 1))) >= 300
cheio &= ndimage.binary_dilation(bom[lb], np.ones((9, 9)))

# o que esta inteiramente sob uma foto ou sob a faixa de cartoes nunca
# aparece: sao respingos verdes das proprias fotos, e so pesariam no arquivo
lab, n = ndimage.label(cheio, structure=np.ones((3, 3)))
caixas = ndimage.find_objects(lab)
tam = np.array(ndimage.sum(cheio, lab, range(1, n + 1)))
fora = np.zeros(n + 1, bool)
for k in range(1, n + 1):
    sy, sx = caixas[k - 1]
    escondido = any(x0 <= sx.start and sx.stop <= x1 + 1 and y0 <= sy.start and sy.stop <= y1 + 1
                    for x0, y0, x1, y1 in TAPADOS)
    fora[k] = not escondido and tam[k - 1] >= 120
cheio = fora[lab]
print('verde %d -> %d px (+%d preenchidos sob a tinta dos textos)'
      % (verde.sum(), cheio.sum(), cheio.sum() - verde.sum()))

up = 4
im = Image.fromarray(np.where(cheio, 0, 255).astype('uint8'))
big = im.resize((W * up, H * up), Image.BICUBIC).filter(ImageFilter.GaussianBlur(up / 2.0))
big.point(lambda v: 255 if v >= 128 else 0).convert('1').save('/tmp/_v.pbm')
subprocess.run(['potrace', '/tmp/_v.pbm', '-s', '-o', '/tmp/_v.svg',
                '-t', '60', '-a', '1.34', '-O', '4.0'], check=True)

svg = open('/tmp/_v.svg').read()
vb = re.search(r'viewBox="([\d.\s]+)"', svg).group(1)
gt = re.search(r'<g transform="([^"]+)"', svg).group(1)
ds = re.findall(r'\sd="([^"]+)"', svg)
out = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="%s" fill="#64A568" '
       'shape-rendering="geometricPrecision">\n'
       '  <!-- curvas do documento; os vaos abertos pela tinta dos textos foram\n'
       '       fechados, para nao sobrar halo em volta das palavras -->\n'
       '<g transform="%s">\n%s\n</g>\n</svg>\n') % (
       vb, gt, '\n'.join('  <path d="%s"/>' % d for d in ds))
open(DEST, 'w').write(out)
print('%s: %d caminhos, %.1f kB' % (DEST, len(ds), len(out) / 1024))
