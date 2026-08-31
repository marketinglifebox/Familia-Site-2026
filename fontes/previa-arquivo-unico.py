# -*- coding: utf-8 -*-
"""Monta uma previa do site inteiro num arquivo HTML so.

Serve para abrir o resultado com dois cliques, sem servidor: as quatro
paginas viram quatro palcos no mesmo documento, e o hash troca entre eles.
Fontes, fotos e SVGs entram como data URIs.

Duas regras que ja quebraram a previa antes, e por isso estao anotadas:

* o url() do CSS vem SEM aspas quando o tailwind e minificado e COM aspas
  quando nao e. O padrao aceita os dois - se ele nao bater, nenhuma fonte
  entra e a previa inteira sai com as fontes do sistema, o que muda toda a
  medida do texto sem dar nenhum erro;

* os hashes das paginas levam o prefixo "pg-". Sem ele, "#valores" bateria
  com o marcador de secao de mesmo nome e cliques.js trataria o link como
  ancora da propria pagina: rolaria, sem trocar de palco.

O arquivo sai com a marca da versao no nome e no titulo: sem isso nao da
para saber, olhando a previa, se ela e a de agora ou uma baixada antes.

Uso:  python3 fontes/previa-arquivo-unico.py
Sai em /tmp/previa-familia-lifebox-<versao>.html
"""
import base64, re, os, subprocess, datetime
ROOT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')+os.sep
def b64(path, mime):
    return 'data:%s;base64,%s'%(mime, base64.b64encode(open(ROOT+path,'rb').read()).decode())
MIME={'.woff2':'font/woff2','.jpg':'image/jpeg','.jpeg':'image/jpeg','.png':'image/png','.svg':'image/svg+xml'}

# ---- 1. CSS com fontes embutidas -------------------------------------------
css=open(ROOT+'assets/css/tailwind.css').read()
# o tailwind minificado escreve url(...) SEM aspas; o nao minificado, com.
# o padrao aceita os dois - senao nenhuma fonte entra e a previa inteira sai
# com as fontes de sistema.
ALVO=re.compile(r"""url\(\s*['"]?(\.\./(?:fonts|img|svg)/[^'")\s]+)['"]?\s*\)""")
def recurso(m):
    rel=m.group(1).replace('../','assets/')
    ext=os.path.splitext(rel)[1]
    return "url('%s')"%b64(rel, MIME[ext])
css, trocas = ALVO.subn(recurso, css)
assert trocas, 'nenhum recurso embutido no CSS - o padrao de url() nao bateu'
print('recursos embutidos no CSS:', trocas)

# ---- 2. paginas -------------------------------------------------------------
def corpo(arquivo, wrapid):
    s=open(ROOT+arquivo).read()
    i=s.index('<div class="stage-wrap"'); j=s.rindex('</div>')+6
    frag=s[i:j]
    frag=frag.replace('id="stageWrap"', 'id="%s"'%wrapid, 1)
    frag=frag.replace('id="stage"', 'id="stage-%s"'%wrapid, 1)
    def sub(m):
        rel=m.group(1); ext=os.path.splitext(rel)[1]
        if not os.path.exists(ROOT+rel):
            # foto ainda nao entregue: mantem o caminho relativo, que falha e
            # dispara o marcador de "sem foto" do carrossel
            return m.group(0)
        return 'src="%s"'%b64(rel, MIME[ext])
    frag=re.sub(r'src="(assets/[^"]+)"', sub, frag)
    return frag

home=corpo('index.html','wrapHome')
quem=corpo('quem-somos.html','wrapQuem')
valo=corpo('valores.html','wrapValo')
trab=corpo('trabalhe-conosco.html','wrapTrab')

# navegacao interna: as quatro paginas viram quatro palcos e o hash troca entre
# eles. O prefixo "pg-" e obrigatorio: sem ele um hash como "#valores" bateria
# com o marcador de secao de mesmo nome, e cliques.js trataria o link como
# ancora da propria pagina - so rolaria, sem trocar de palco.
def liga(frag):
    frag=re.sub(r'href="quem-somos\.html#([\w-]+)"', r'href="#pg-quem!\1"', frag)
    frag=frag.replace('href="quem-somos.html"','href="#pg-quem"')
    frag=re.sub(r'href="valores\.html#([\w-]+)"',    r'href="#pg-valores!\1"', frag)
    frag=frag.replace('href="valores.html"','href="#pg-valores"')
    frag=frag.replace('href="trabalhe-conosco.html"','href="#pg-trabalhe"')
    frag=frag.replace('href="index.html"','href="#pg-home"')
    # ancoras da propria pagina continuam sendo ancoras
    return frag
home, quem, valo, trab = liga(home), liga(quem), liga(valo), liga(trab)

js_main=open(ROOT+'assets/js/main.js').read()
js_hab=open(ROOT+'assets/js/habitos.js').read()
js_pil=open(ROOT+'assets/js/pilares.js').read()
js_tra=open(ROOT+'assets/js/transicao.js').read()
js_nav=open(ROOT+'assets/js/cliques.js').read()
js_car=open(ROOT+'assets/js/carrossel.js').read()
js_ben=open(ROOT+'assets/js/beneficios.js').read()
js_val=open(ROOT+'assets/js/valores.js').read()
# caminhos de imagem dentro do JS viram data URIs
def jsimg(m):
    rel=m.group(1); ext=os.path.splitext(rel)[1]
    if not os.path.exists(ROOT+rel):   # foto ainda nao entregue: usa a padrao
        rel='assets/img/pilar-main.jpg'; ext='.jpg'
    return "'%s'"%b64(rel, MIME[ext])
js_pil=re.sub(r"'(assets/img/[^']+)'", jsimg, js_pil)
# colapsa data URIs repetidas numa unica variavel (o mapa aponta varias
# vezes para a mesma foto enquanto as definitivas nao chegam)
from collections import Counter
uris=re.findall(r"'(data:image/[^']+)'", js_pil)
for i,(u,n) in enumerate(Counter(uris).items()):
    if n>1:
        js_pil = ("var __img%d=%s;\n"%(i,repr(u))) + js_pil.replace("'"+u+"'", "__img%d"%i)
# main.js precisa lidar com dois palcos
js_main=js_main.replace("var stage = document.getElementById('stage');","var stage = null;")
js_main=js_main.replace("var wrap  = document.getElementById('stageWrap');","var wrap  = null;")

# marca da versao: hash do commit + data, para dar para conferir de olho qual
# previa esta aberta
try:
    VERSAO=subprocess.check_output(['git','-C',ROOT,'rev-parse','--short','HEAD'],
                                   text=True).strip()
except Exception:
    VERSAO='sem-git'
DATA=datetime.date.today().isoformat()
MARCA='%s %s'%(DATA, VERSAO)

out=[]
out.append('<meta charset="utf-8">')
out.append('<title>Família Lifebox — prévia %s</title>'%MARCA)
out.append('<style>\n%s\n</style>'%css)
out.append('<style>.stage-wrap[hidden]{display:none}'
           'img{max-width:none}'   # alguns visualizadores impoem max-width:100%
           '.marca-previa{position:fixed;left:8px;bottom:8px;z-index:2147483647;'
           'font:11px/1 system-ui,sans-serif;color:#8a8078;background:rgba(253,246,239,.85);'
           'padding:4px 7px;border-radius:4px;pointer-events:none}</style>')
out.append('<div class="marca-previa">prévia %s</div>'%MARCA)
out.append(home)
out.append(quem.replace('<div class="stage-wrap" id="wrapQuem"','<div class="stage-wrap" id="wrapQuem" hidden',1))
out.append(valo.replace('<div class="stage-wrap" id="wrapValo"','<div class="stage-wrap" id="wrapValo" hidden',1))
out.append(trab.replace('<div class="stage-wrap" id="wrapTrab"','<div class="stage-wrap" id="wrapTrab" hidden',1))
out.append('''<script>
/* --- escala dos dois palcos + navegacao entre as paginas ------------------ */
(function(){
  var paginas=[{wrap:'wrapHome',stage:'stage-wrapHome',h:5577},
               {wrap:'wrapQuem',stage:'stage-wrapQuem',h:3486},
               {wrap:'wrapValo',stage:'stage-wrapValo',h:2832},
               {wrap:'wrapTrab',stage:'stage-wrapTrab',h:2310}];
  function ajusta(){
    paginas.forEach(function(p){
      var w=document.getElementById(p.wrap), s=document.getElementById(p.stage);
      if(!w||!s||w.hidden) return;
      var k=w.clientWidth/1512;
      s.style.setProperty('--k',k);
      w.style.height=(p.h*k)+'px';
    });
  }
  function mostra(id, secao){
    paginas.forEach(function(p){ document.getElementById(p.wrap).hidden = (p.wrap!==id); });
    ajusta();
    var alvo = secao && document.getElementById(secao);
    if (alvo) window.scrollTo(0, alvo.getBoundingClientRect().top + window.scrollY);
    else window.scrollTo(0,0);
    /* as fileiras que estavam escondidas mediram tudo como zero: reenquadra */
    if (window.Carrosseis) window.Carrosseis.forEach(function(c){ c.centraliza(); });
    /* aqui nao ha recarga: a bola que cobriu a tela e desfeita na sequencia */
    if (window.Transicao) window.Transicao.revela();
  }
  var destino={'pg-quem':'wrapQuem','pg-valores':'wrapValo','pg-trabalhe':'wrapTrab',
               'pg-home':'wrapHome'};
  /* cliques.js entrega a navegacao aqui em vez de mexer em location: dentro de
     um iframe com sandbox - que e como esta previa costuma ser aberta - trocar
     location.hash nao e salto de ancora, e uma renavegacao do quadro, e ela
     mata a pagina. Trocar de palco na mao nao depende de nada disso. */
  window.Roteador=function(alvo){
    if(!alvo || alvo.charAt(0)!=='#') return false;
    var partes=alvo.slice(1).split('!');
    var wrap=destino[partes[0]];
    if(!wrap) return false;
    mostra(wrap, partes[1]);
    return true;
  };
  /* rede: qualquer link de pagina que cliques.js nao intercepte - o logo do
     cabecalho, por exemplo - tambem troca de palco aqui, em vez de deixar o
     navegador mexer no location */
  document.addEventListener('click', function(e){
    if (e.defaultPrevented) return;                 /* cliques.js ja assumiu */
    if (e.metaKey||e.ctrlKey||e.shiftKey||e.altKey||e.button!==0) return;
    var a=e.target;
    while (a && a.nodeName!=='A') a=a.parentNode;
    if (!a || !a.getAttribute) return;
    var h=a.getAttribute('href')||'';
    /* o logo da propria pagina inicial aponta para "#": no navegador comum
       isso so volta ao topo, mas dentro de um iframe com sandbox e mais uma
       renavegacao do quadro */
    if (h==='#'){ e.preventDefault(); window.scrollTo(0,0); return; }
    if (window.Roteador(h)) e.preventDefault();
  });
  function rota(){
    var partes=(location.hash||'').replace('#','').split('!');
    mostra(destino[partes[0]] || 'wrapHome', partes[1]);
  }
  window.addEventListener('hashchange',rota);
  window.addEventListener('resize',ajusta,{passive:true});
  if(document.fonts&&document.fonts.ready) document.fonts.ready.then(ajusta);
  rota();
})();
</script>''')
out.append('<script>\n%s\n</script>'%js_hab)
out.append('<script>\n%s\n</script>'%js_pil)
out.append('<script>\n%s\n</script>'%js_tra)
out.append('<script>\n%s\n</script>'%js_nav)
out.append('<script>\n%s\n</script>'%js_car)
out.append('<script>\n%s\n</script>'%js_ben)
out.append('<script>\n%s\n</script>'%js_val)
SAIDA='/tmp/previa-familia-lifebox-%s.html'%VERSAO
open(SAIDA,'w').write('\n'.join(out))
print('%s  (%d bytes, %s)'%(SAIDA, os.path.getsize(SAIDA), MARCA))
