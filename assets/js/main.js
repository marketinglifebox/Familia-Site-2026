/* ==========================================================================
   Escala o palco para a largura da viewport, preservando exatamente as
   proporcoes do documento original. A altura vem do proprio palco - cada
   pagina tem a sua (5577, 3486 e 2832 px) - e nao de um numero fixo.
   ========================================================================== */
(function () {
  'use strict';

  var DESIGN_W = 1512;
  var DESIGN_H = 5577;      /* so como reserva, se o palco ainda nao mediu */

  /* Teto da escala. O documento e uma prancha de apresentacao: a 100% o menu
     tem 24,5px, o texto corrido 29px e os titulos de 49 a 112px - quase o
     dobro da medida de um site, porque foi desenhado para ser visto como
     pagina, nao lido a distancia de monitor. A 0,8 isso vira menu de 19,6px e
     texto de 23px, que e a medida em que se le sentado. As proporcoes nao
     mudam: e a prancha inteira que encolhe.

     Quem for reconferir a fidelidade contra o PDF precisa da prancha em 100%:
     defina window.TETO_ESCALA = 1 antes deste arquivo. */
  var TETO_K = window.TETO_ESCALA || 0.8;

  var stage = document.getElementById('stage');
  var wrap  = document.getElementById('stageWrap');
  if (!stage || !wrap) return;

  /* Nunca passa de 1: acima disso a pagina nao ficaria maior, ficaria ampliada
     - o desenho tem 1512px de largura, e esticar alem disso e o mesmo que dar
     zoom, com o texto grande demais para a distancia de leitura. Numa tela mais
     larga o palco fica no tamanho desenhado e centralizado. */
  function resize() {
    var k = Math.min(TETO_K, wrap.clientWidth / DESIGN_W);
    var sobra = Math.max(0, wrap.clientWidth - DESIGN_W * k);
    stage.style.setProperty('--k', k);
    stage.style.setProperty('--dx', (sobra / 2).toFixed(2) + 'px');
    /* quanto cada faixa de fundo precisa transbordar para os lados, ja em
       pixels do projeto, para encostar na borda da tela mesmo com o palco
       centralizado */
    stage.style.setProperty('--sangra', (sobra / 2 / k).toFixed(2) + 'px');
    wrap.style.height = ((stage.offsetHeight || DESIGN_H) * k) + 'px';
  }

  /* O palco e maior que o wrap (a escala e transform, que nao muda a altura de
     layout), entao o wrap e rolavel por dentro. Uma navegacao por ancora rola
     os ancestrais rolaveis e empurraria o palco para fora do lugar; aqui ele
     volta na hora. */
  wrap.addEventListener('scroll', function () {
    if (wrap.scrollTop || wrap.scrollLeft) { wrap.scrollTop = 0; wrap.scrollLeft = 0; }
  }, { passive: true });

  resize();
  window.addEventListener('resize', resize, { passive: true });
  if (window.ResizeObserver) new ResizeObserver(resize).observe(document.body);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(resize);
})();
