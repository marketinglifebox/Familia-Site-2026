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
TAPADOS = [(284, 630, 1271, 1123), (279, 1452, 1266, 1944)]

# A fileira de valores virou carrossel, entao o que estava atras dos cartoes
# deixou de ficar escondido para sempre. Os tracos que entram na faixa sao
# remontados ate onde a medida alcanca; os que nao reaparecem embaixo terminam
# em ponta dentro da faixa, como os outros tracos deste desenho.
FAIXA = (2362, 2620)

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

# --- tracos que atravessam a faixa dos cartoes -------------------------------
def corridas(linha):
    xs = np.where(linha)[0]
    if not len(xs): return []
    saida, ini, ant = [], xs[0], xs[0]
    for x in xs[1:]:
        if x - ant > 4: saida.append((ini, ant)); ini = x
        ant = x
    saida.append((ini, ant))
    return saida

def segue(cheio, y0, passo, limite, a, b):
    """acompanha uma corrida linha a linha e devolve (y, centro, largura)"""
    amostras, ca, cb = [], a, b
    for k in range(limite):
        y = y0 + passo * k
        if not (0 <= y < cheio.shape[0]): break
        cs = [(i, j) for i, j in corridas(cheio[y]) if j >= ca - 14 and i <= cb + 14]
        if not cs: break
        i0 = min(i for i, _ in cs); j0 = max(j for _, j in cs)
        if j0 - i0 > (cb - ca) * 2.4 + 40: break        # cruzou com outro traco
        amostras.append((y, (i0 + j0) / 2.0, j0 - i0 + 1)); ca, cb = i0, j0
    return np.array(amostras) if len(amostras) > 12 else None

def reta(d):
    """posicao e inclinacao no extremo mais proximo da faixa"""
    n = min(80, len(d))
    p = np.polyfit(d[:n, 0], d[:n, 1], 1)
    return p, float(np.median(d[:n, 2]))

def atravessa(cheio):
    """continua, dentro da faixa dos cartoes, os tracos que entram nela.

    Onde o traco reaparece do outro lado, os dois lados sao costurados e ele
    fica inteiro. Onde nao reaparece - porque no documento aquele trecho estava
    tapado o tempo todo - ele segue pela tangente e termina em ponta, como os
    outros tracos deste desenho. Cada traco e continuado em reta: sobre 260 px
    a curvatura destas curvas e pequena, e extrapolar parabola daria disparate.
    """
    ya, yb = FAIXA
    saida = cheio.copy()

    entradas = [segue(cheio, ya - 3, -1, 200, a, b) for a, b in corridas(cheio[ya - 3])]
    saidas   = [segue(cheio, yb + 3, +1, 200, a, b) for a, b in corridas(cheio[yb + 3])]
    entradas = [d for d in entradas if d is not None]
    saidas   = [d for d in saidas   if d is not None]

    # pedacos que aparecem nos vaos entre um cartao e outro
    meio = cheio.copy(); meio[:ya + 5] = False; meio[yb - 4:] = False
    lab, n = ndimage.label(meio, structure=np.ones((3, 3)))
    caixas = ndimage.find_objects(lab)
    # Um pedaco desses aparece so pela fresta entre dois cartoes, cortado dos
    # dois lados: o centro linha a linha nao vale nada. O que vale e o tempo de
    # travessia - quantas linhas o traco leva para cruzar a fresta - que da a
    # inclinacao: (largura da fresta + largura do traco) / linhas gastas.
    pedacos = []
    for k in range(1, n + 1):
        if (lab == k).sum() < 250: continue
        sy, sx = caixas[k - 1]
        ys, xs = np.where(lab == k)
        y0, y1 = int(ys.min()), int(ys.max())
        x0, x1 = int(xs.min()), int(xs.max())
        if y1 - y0 < 8: continue
        cima  = xs[ys == y0].mean(); baixo = xs[ys == y1].mean()
        pedacos.append(dict(y=(y0 + y1) / 2.0, x=(x0 + x1) / 2.0,
                            larg=x1 - x0 + 1, linhas=y1 - y0,
                            sinal=1.0 if baixo > cima else -1.0,
                            m=(x1 - x0 + 1) / (y1 - y0) * (1 if baixo > cima else -1)))

    def pinta(y0, y1, f, lg, ponta_em=None):
        ys = np.arange(min(y0, y1), max(y0, y1) + 1, dtype=float)
        xs = f(ys)
        larg = np.full(len(ys), lg)
        if ponta_em is not None:
            larg = lg * np.clip(np.abs(ys - ponta_em) / 90.0, 0, 1) ** 0.6
        for y, x, wv in zip(ys.astype(int), xs, larg):
            if wv <= 1 or not (ya <= y <= yb): continue
            xa = int(round(x - wv / 2)); xb2 = int(round(x + wv / 2))
            if xb2 < 0 or xa >= W: continue
            saida[y, max(0, xa):min(W, xb2 + 1)] = True

    def hermite(y0, y1, x0, x1, m0, m1):
        def f(ys):
            t = (ys - y0) / (y1 - y0)
            h00 = 2*t**3 - 3*t**2 + 1; h10 = t**3 - 2*t**2 + t
            h01 = -2*t**3 + 3*t**2;    h11 = t**3 - t**2
            return h00*x0 + h10*m0*(y1-y0) + h01*x1 + h11*m1*(y1-y0)
        return f

    usados = set()
    for d in entradas:
        pe, lg = reta(d)
        y0 = float(d[0, 0]); x0 = np.polyval(pe, y0)
        # a quem este traco se liga: quem sai por baixo, ou um pedaco de vao
        melhor = None
        for tipo, k, dd in ([('saida', k, x) for k, x in enumerate(saidas)] +
                            [('pedaco', k, x) for k, x in enumerate(pedacos)]):
            if (tipo, k) in usados: continue
            ym = float(dd['y'] if tipo == 'pedaco' else dd[0, 0])
            xm = float(dd['x'] if tipo == 'pedaco' else dd[0, 1])
            erro = abs(np.polyval(pe, ym) - xm)
            limite = 200 if tipo == 'pedaco' else 70
            if erro < limite and (melhor is None or erro < melhor[0]):
                melhor = (erro, tipo, k, dd, ym, xm)
        if melhor is None:
            xf = np.polyval(pe, yb)
            sai = not (-lg < xf < W + lg)
            pinta(ya, yb, lambda ys: np.polyval(pe, ys), lg, None if sai else yb)
            continue
        _, tipo, k, dd, ym, xm = melhor
        usados.add((tipo, k))
        if tipo == 'saida':
            pd, _ = reta(dd)
            pinta(ya, yb, hermite(y0, ym, x0, xm, pe[0], pd[0]), lg)
        else:                                  # passa pela fresta e segue reto
            # a largura do traco entra na conta da travessia
            larguraF = dd['larg']
            m1 = (larguraF + lg) / dd['linhas'] * dd['sinal']
            pinta(ya, int(ym), hermite(y0, ym, x0, xm, pe[0], m1), lg)
            pinta(int(ym), yb, lambda ys: xm + m1 * (ys - ym), lg, yb)

    for k, dd in enumerate(pedacos):           # fresta sem dono: abre dos dois lados
        if ('pedaco', k) in usados: continue
        f = lambda ys, dd=dd: dd['x'] + dd['m'] * (ys - dd['y'])
        pinta(ya, int(dd['y']), f, 30.0, ya)
        pinta(int(dd['y']), yb, f, 30.0, yb)
    return saida

antes = cheio.sum()
cheio = atravessa(cheio)
print('faixa dos cartoes: +%d px de traco remontado' % (cheio.sum() - antes))

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
