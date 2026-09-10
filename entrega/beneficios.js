/* ==========================================================================
   "Benefícios Lifebox" — carrossel contínuo.

   O mecanismo (laço infinito, arrasto, roda, teclado e laterais desfocadas)
   está em carrossel.js. Aqui ficam só as duas coisas próprias desta fileira:
   os benefícios cuja foto ainda não chegou e os rótulos longos demais.
   ========================================================================== */
(function () {
  'use strict';

  var caixa  = document.getElementById('benefCarrossel');
  var trilho = document.getElementById('benefTrilho');
  if (!caixa || !trilho || !window.Carrossel) return;

  /* --- textos longos --------------------------------------------------- */
  /* o documento nunca passa de ~346px de tinta num título ("SELEÇÃO DE") nem
     de ~305px num subtítulo; os benefícios novos que passam disso encolhem o
     suficiente para caber, em vez de invadir o cartão vizinho */
  var lona = document.createElement('canvas').getContext('2d');

  function tinta(el, e) {
    lona.font = e.fontStyle + ' ' + e.fontWeight + ' ' + e.fontSize + ' ' + e.fontFamily;
    var esp = parseFloat(e.letterSpacing) || 0;          /* canvas ignora o tracking */
    return lona.measureText(el.textContent).width + esp * el.textContent.length;
  }

  function encolhe(sel, teto) {
    Array.prototype.forEach.call(trilho.querySelectorAll(sel), function (el) {
      el.style.fontSize = '';
      var e = getComputedStyle(el);
      var w = tinta(el, e);
      if (w > teto) el.style.fontSize = (parseFloat(e.fontSize) * teto / w).toFixed(2) + 'px';
    });
  }

  function ajustaTextos() {
    encolhe('.benef-titulo', 346);
    encolhe('.benef-sub', 305);
  }
  ajustaTextos();

  /* posição inicial: um cartão assomando à esquerda, como no documento
     (o recuo é medido a partir do início do bloco do meio) */
  /* a fileira anda sozinha (80 px/s) para as dezessete fotos passarem pela
     tela sem exigir arrasto; ela para assim que o ponteiro encosta */
  var carrossel = window.Carrossel(caixa, trilho,
                                   { recuo: -159, passo: 447, desliza: 80 });

  /* --- fotos ainda não entregues --------------------------------------- */
  /* doze benefícios ainda não têm foto e mostram, no lugar dela, um ícone
     desenhado a partir do próprio título. O caminho da foto definitiva fica
     em data-foto: assim que o arquivo existir, ele entra sozinho no lugar do
     ícone - sem mexer no HTML. A troca só acontece depois que a foto carrega,
     para o quadro nunca piscar vazio.

     Roda depois da triplicação do carrossel para alcançar também as cópias. */
  Array.prototype.forEach.call(trilho.querySelectorAll('.benef-foto img'), function (img) {
    function falta() { img.parentNode.classList.add('sem-foto'); }
    img.addEventListener('error', falta);
    if (img.complete && !img.naturalWidth) falta();

    var foto = img.getAttribute('data-foto');
    if (!foto) return;
    var sonda = new Image();
    sonda.onload = function () { img.src = foto; };
    sonda.src = foto;
  });

  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () {
    ajustaTextos();
    carrossel.centraliza();
  });
})();
