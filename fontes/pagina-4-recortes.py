# -*- coding: utf-8 -*-
"""Recortes da pagina 4 ("Trabalhe conosco").

O PDF da pagina 4, como os outros, e uma pilha de JPEGs achatados a 757px de
largura; o site trabalha na prancha de 1512px, entao tudo aqui e medido sobre
a pagina renderizada em 2x. Deste arquivo saem tres pecas:

1. assets/img/trabalhe-fundo.jpg
   A ilustracao verde e as sombras dos cartoes de vaga, ou seja, tudo o que
   nao da para redesenhar. O conteudo que o HTML repinta por cima - o cartao
   laranja da chamada, os titulos, os precos, as descricoes e os botoes - e
   coberto com o creme da pagina, para nao aparecer duas vezes.

2. assets/svg/titulo-trabalhe.svg
   O letreiro "TRABALHE CONOSCO". Ele e desenhado a mao no documento: as
   letras se montam umas sobre as outras e cada uma abre um vao na anterior,
   com espacamento diferente em cada par. Nenhuma fonte com um so tracking
   reproduz isso, entao o letreiro vem tracado - o texto continua no <h1>.

3. assets/svg/lupa.svg
   O icone de busca, tambem tracado (é desenho, nao tipografia).
"""
import subprocess, tempfile, os
import numpy as np
from PIL import Image
import pymupdf

PDF   = os.environ.get('PDF_PAGINA_4', 'pagina_4_trabalhe_conosco_.pdf')
RAIZ  = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
CREME = np.array([253, 246, 239])
LARAN = np.array([232, 101,  50])

# ---------------------------------------------------------------- a pagina --
doc = pymupdf.open(PDF)
pag = doc[0]
esc = 1512 / pag.rect.width
pix = pag.get_pixmap(matrix=pymupdf.Matrix(esc, esc))
A = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, pix.n)[:, :, :3]
A = np.array(A[:2310, :1512], dtype=np.uint8)

# ------------------------------------------------------- 1. fundo da pagina --
# a ilustracao so comeca em y=814; acima disso a pagina e creme lisa
Y0 = 814
fundo = A[Y0:2310].copy()

def apaga(x0, y0, x1, y1):
    """cobre com o creme da pagina o que o HTML redesenha por cima"""
    fundo[y0 - Y0:y1 - Y0, x0:x1] = CREME

apaga(184, 471, 1322, 893)                       # cartao laranja da chamada
for topo in (961, 1395, 1827):                   # conteudo dos tres cartoes
    apaga(200, topo + 55, 1290, topo + 120)      #   titulo e preco
    apaga(200, topo + 160, 1290, topo + 220)     #   descricao
    apaga(200, topo + 245, 620, topo + 335)      #   botao
Image.fromarray(fundo).save(os.path.join(RAIZ, 'assets/img/trabalhe-fundo.jpg'),
                            quality=88, optimize=True, progressive=False)

# ------------------------------------------------------------- 2. e 3. SVGs --
def traca(x0, y0, x1, y1, fim, cor, tinta, fundo_cor, amp=4, turd=8):
    """mascara de tinta -> potrace -> SVG com o viewBox no tamanho do recorte"""
    d = tinta - fundo_cor
    rec = A[y0:y1, x0:x1].astype(float)
    alfa = ((rec - fundo_cor) * d).sum(2) / (d * d).sum()
    grande = Image.fromarray((np.clip(alfa, 0, 1) * 255).astype('uint8')) \
                  .resize(((x1 - x0) * amp, (y1 - y0) * amp), Image.LANCZOS)
    m = np.asarray(grande) > 127
    with tempfile.TemporaryDirectory() as tmp:
        pbm = os.path.join(tmp, 'm.pbm'); svg = os.path.join(tmp, 'm.svg')
        Image.fromarray(((~m) * 255).astype('uint8')).save(pbm)
        subprocess.run(['potrace', '-s', '-o', svg, '--turdsize', str(turd),
                        '--alphamax', '1.0', '--opttolerance', '0.2', pbm], check=True)
        s = open(svg).read()
    corpo = s[s.index('<g transform'):s.rindex('</svg>')].replace('fill="#000000"', 'fill="%s"' % cor)
    # o viewBox do potrace vem no tamanho em pixels da imagem ampliada
    open(os.path.join(RAIZ, fim), 'w').write(
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" '
        'preserveAspectRatio="none" aria-hidden="true" focusable="false">\n%s</svg>\n'
        % ((x1 - x0) * amp, (y1 - y0) * amp, x1 - x0, y1 - y0, corpo))

traca(183, 311, 1323, 402, 'assets/svg/titulo-trabalhe.svg', '#FDF6EF', CREME, LARAN)
traca(299, 736,  343, 780, 'assets/svg/lupa.svg',            '#E86532', LARAN, np.array([253, 247, 242]),
      amp=8, turd=20)
print('pronto')
