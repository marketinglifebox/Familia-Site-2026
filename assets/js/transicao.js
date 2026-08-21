/* ==========================================================================
   Transição entre páginas — a mesma bola que cresce do painel de
   "Nossos hábitos", agora do tamanho da tela.

   Ao clicar, um círculo laranja nasce no ponto do clique e cresce até cobrir
   tudo; a página seguinte já abre coberta e o círculo encolhe de volta para
   o mesmo ponto, revelando-a. Como o ponto atravessa a troca de página pelo
   sessionStorage, o movimento é um só, sem corte no meio.

   O círculo é um ::before do <html> (ver .transicao no CSS): assim ele já
   existe antes da primeira pintura da página nova, e não há aquele lampejo
   do conteúdo antes da cobertura.
   ========================================================================== */
window.Transicao = (function () {
  'use strict';

  var CHAVE   = 'transicao';
  var ESPERA  = 110;   /* ms antes de a bola sair — dá para ver o toque no botão */
  var COBRE   = 430;   /* ms de crescimento (igual ao CSS) */
  var TETO    = 700;   /* ms: tempo máximo esperando a página nova assentar */
  var raiz    = document.documentElement;
  var parado  = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function ponto(x, y) {
    raiz.style.setProperty('--tx', (x / window.innerWidth * 100).toFixed(2));
    raiz.style.setProperty('--ty', (y / window.innerHeight * 100).toFixed(2));
  }

  /* --- sair: a bola cresce e cobre a tela ------------------------------- */
  function sai(x, y, feito) {
    if (parado) { feito(); return; }
    ponto(x, y);
    try {
      sessionStorage.setItem(CHAVE, (x / window.innerWidth * 100).toFixed(2) + ',' +
                                    (y / window.innerHeight * 100).toFixed(2));
    } catch (_) {}
    /* os dois passos vao em relogios separados, e nao em requestAnimationFrame:
       numa aba em segundo plano o rAF nao dispara, e o link ficaria morto.
       O intervalo entre eles e so para o navegador registrar a escala 0 antes
       de mudar para 1 - sem isso nao ha o que transicionar. */
    setTimeout(function () {
      raiz.classList.add('transicao');
      setTimeout(function () { raiz.classList.add('cobre'); }, 24);
      setTimeout(feito, COBRE + 24);
    }, ESPERA);
  }

  /* --- revelar: a bola encolhe de volta para o mesmo ponto --------------- */
  function revela() {
    try { sessionStorage.removeItem(CHAVE); } catch (_) {}
    if (!raiz.classList.contains('transicao')) return;
    setTimeout(function () {
      raiz.classList.remove('chega', 'cobre');       /* volta a escala 0, com transição */
      setTimeout(function () { raiz.classList.remove('transicao'); }, 700);
    }, 24);
  }

  /* Ao abrir uma página que veio de um clique, espera ela assentar (as fontes
     mudam a medida do texto e o palco é redimensionado no carregamento) e só
     então revela. */
  function aoChegar() {
    if (!raiz.classList.contains('chega')) {
      try { sessionStorage.removeItem(CHAVE); } catch (_) {}
      return;
    }
    var feito = false;
    function agora() { if (!feito) { feito = true; revela(); } }
    setTimeout(agora, TETO);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(agora);
    else window.addEventListener('load', agora);
  }

  /* voltando pelo histórico o navegador restaura a página como ela estava;
     se ela tiver sido guardada no meio da transição, a bola voltaria junto */
  window.addEventListener('pageshow', function (e) {
    if (e.persisted) raiz.classList.remove('transicao', 'cobre', 'chega');
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', aoChegar);
  } else {
    aoChegar();
  }

  return { sai: sai, revela: revela };
})();
