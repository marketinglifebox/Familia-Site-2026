# -*- coding: utf-8 -*-
"""Monta a pasta de entrega: o site inteiro em HTML, CSS e JS, num nivel so.

O repositorio guarda o projeto organizado - assets/css, assets/js, assets/img,
assets/svg, assets/fonts, mais o src/ do Tailwind e os scripts de fontes/. Para
entregar, nada disso e preciso: basta o que o navegador le. Este script copia
esses arquivos para entrega/ sem nenhuma subpasta e reescreve todos os
caminhos - nos HTML, dentro do CSS e nas strings do JS.

Nao ha build: o CSS ja vai compilado, entao a pasta abre direto no navegador e
sobe para qualquer hospedagem estatica como esta.

    python3 fontes/montar-entrega.py
"""
import os
import re
import shutil

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DESTINO = os.path.join(RAIZ, 'entrega')
PAGINAS = ['index.html', 'quem-somos.html', 'valores.html', 'trabalhe-conosco.html']
CSS_ENTRADA = 'assets/css/tailwind.css'
CSS_SAIDA = 'estilo.css'

LEIA_ME = """SITE FAMILIA LIFEBOX
====================

Tudo o que o navegador precisa esta nesta pasta, num nivel so, sem subpastas
e sem nenhuma etapa de build.

  index.html ............ pagina inicial
  quem-somos.html ....... quem somos / habitos e rituais
  valores.html .......... missao, visao e valores
  trabalhe-conosco.html . vagas

  estilo.css ............ folha de estilo unica, ja compilada
  *.js .................. os comportamentos (carrosseis, transicoes, painel
                          de habitos, escala do palco)
  *.woff2 ............... as fontes, servidas da propria pasta
  *.jpg *.png *.svg ..... imagens e vetores

COMO USAR
---------
Para publicar: suba o conteudo desta pasta para a raiz do site. Qualquer
hospedagem de arquivos estaticos serve.

Para abrir no computador: prefira servir por HTTP em vez de dar dois cliques
no arquivo. Abrindo por file:// o navegador bloqueia as fontes por politica de
origem e a pagina aparece com as fontes trocadas. Um jeito rapido:

    python3 -m http.server 8000

e abrir http://localhost:8000

TROCAR UMA IMAGEM
-----------------
Basta substituir o arquivo mantendo o mesmo nome. As fotos dos beneficios que
ainda faltam entram sozinhas ao serem gravadas como ben-<nome>.jpg.
"""


def main():
    if os.path.isdir(DESTINO):
        shutil.rmtree(DESTINO)
    os.makedirs(DESTINO)

    # 1. o mapa de caminho antigo -> nome plano. Nao ha colisao de nome base
    #    entre as pastas de assets, entao o proprio nome do arquivo serve.
    mapa = {}
    for pasta, _, arquivos in os.walk(os.path.join(RAIZ, 'assets')):
        for a in arquivos:
            inteiro = os.path.join(pasta, a)
            rel = os.path.relpath(inteiro, RAIZ).replace(os.sep, '/')
            plano = CSS_SAIDA if rel == CSS_ENTRADA else a
            if plano in mapa.values() and rel != CSS_ENTRADA:
                raise SystemExit('colisao de nome: ' + plano)
            mapa[rel] = plano
            shutil.copy2(inteiro, os.path.join(DESTINO, plano))

    # Vale para qualquer caminho de asset, inclusive os arquivos que ainda nao
    # chegaram - as fotos que faltam nos beneficios e os icones dos valores.
    # Se so trocassemos os que existem, esses ficariam apontando para uma
    # subpasta que a entrega nao tem, e nunca entrariam ao serem gravados.
    EXT = r'jpg|jpeg|png|svg|woff2|css|js'
    DE_ASSETS = re.compile(r'assets/(?:[\w-]+/)+([\w.-]+\.(?:%s))' % EXT)
    DE_CSS    = re.compile(r'\.\./(?:[\w-]+/)+([\w.-]+\.(?:%s))' % EXT)

    def achata(texto):
        """Troca todo caminho de asset pelo nome plano, nas duas formas que
        aparecem: 'assets/img/x.jpg' nos HTML e no JS, '../img/x.jpg' no CSS.
        O CSS compilado do Tailwind e o unico que muda de nome."""
        texto = texto.replace(CSS_ENTRADA, CSS_SAIDA)
        texto = DE_ASSETS.sub(lambda m: m.group(1), texto)
        texto = DE_CSS.sub(lambda m: m.group(1), texto)
        return texto

    # 2. as paginas
    for p in PAGINAS:
        s = open(os.path.join(RAIZ, p), encoding='utf-8').read()
        open(os.path.join(DESTINO, p), 'w', encoding='utf-8').write(achata(s))

    # 3. o CSS e os JS ja copiados, agora com os caminhos reescritos
    for nome in os.listdir(DESTINO):
        if nome.endswith(('.css', '.js')):
            caminho = os.path.join(DESTINO, nome)
            s = open(caminho, encoding='utf-8').read()
            open(caminho, 'w', encoding='utf-8').write(achata(s))

    open(os.path.join(DESTINO, 'LEIA-ME.txt'), 'w', encoding='utf-8').write(LEIA_ME)

    arquivos = sorted(os.listdir(DESTINO))
    tamanho = sum(os.path.getsize(os.path.join(DESTINO, f)) for f in arquivos)
    print('entrega/ montada: %d arquivos, %.1f MB' % (len(arquivos), tamanho / 1e6))
    for ext in ('.html', '.css', '.js', '.woff2', '.jpg', '.png', '.svg', '.txt'):
        n = len([f for f in arquivos if f.endswith(ext)])
        if n:
            print('   %-7s %d' % (ext, n))


if __name__ == '__main__':
    main()
