/* ==========================================================================
   Escala o palco de 1512x5577px para a largura da viewport, preservando
   exatamente as proporcoes do documento original.
   ========================================================================== */
(function () {
  'use strict';

  var DESIGN_W = 1512;
  var DESIGN_H = 5577;

  var stage = document.getElementById('stage');
  var wrap  = document.getElementById('stageWrap');
  if (!stage || !wrap) return;

  function resize() {
    var k = wrap.clientWidth / DESIGN_W;
    stage.style.setProperty('--k', k);
    wrap.style.height = (DESIGN_H * k) + 'px';
  }

  resize();
  window.addEventListener('resize', resize, { passive: true });
  if (window.ResizeObserver) new ResizeObserver(resize).observe(document.body);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(resize);
})();
