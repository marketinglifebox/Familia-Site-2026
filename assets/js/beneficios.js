/* ==========================================================================
   "Benefícios Lifebox" — carrossel contínuo.

   A fileira corre para os dois lados: arrastando com o mouse, com o dedo,
   com a roda ou pelo teclado. O conteúdo é triplicado e a posição volta ao
   bloco do meio sempre que chega perto de uma ponta, de modo que nunca há
   fim — sempre aparecem mais benefícios dos dois lados.
   ========================================================================== */
(function () {
  'use strict';

  var caixa   = document.getElementById('benefCarrossel');
  var trilho  = document.getElementById('benefTrilho');
  if (!caixa || !trilho) return;

  /* --- triplica os cartões para o laço ---------------------------------- */
  var originais = Array.prototype.slice.call(trilho.children);
  function bloco() {
    var frag = document.createDocumentFragment();
    originais.forEach(function (c) {
      var copia = c.cloneNode(true);
      copia.setAttribute('aria-hidden', 'true');
      copia.querySelectorAll('img').forEach(function (i) { i.alt = ''; });
      frag.appendChild(copia);          /* mantém a ordem original */
    });
    return frag;
  }
  trilho.insertBefore(bloco(), trilho.firstChild);   /* cópia à esquerda */
  trilho.appendChild(bloco());                       /* cópia à direita  */

  /* --- fotos ainda não entregues --------------------------------------- */
  /* alguns benefícios ainda não têm foto; nesses o quadro recebe a marca da
     casa em vez do ícone de imagem quebrada. Roda depois da triplicação para
     alcançar também as cópias. */
  Array.prototype.forEach.call(trilho.querySelectorAll('.benef-foto img'), function (img) {
    function falta() { img.parentNode.classList.add('sem-foto'); }
    img.addEventListener('error', falta);
    if (img.complete && !img.naturalWidth) falta();
  });

  /* --- textos longos --------------------------------------------------- */
  /* o documento nunca passa de ~346px de tinta num titulo ("SELEÇÃO DE") nem
     de ~305px num subtitulo; os beneficios novos que passam disso encolhem o
     suficiente para caber, em vez de invadir o cartao vizinho */
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

  var umBloco = 0;
  function medir() {
    umBloco = trilho.scrollWidth / 3;
  }

  /* posição inicial: bloco do meio, com um cartão assomando à esquerda,
     como no documento */
  function centraliza() {
    medir();
    caixa.scrollLeft = umBloco - 124;
    pinta();
  }

  function reenquadra() {
    if (!umBloco) return;
    if (caixa.scrollLeft < umBloco * 0.5)      caixa.scrollLeft += umBloco;
    else if (caixa.scrollLeft > umBloco * 1.5) caixa.scrollLeft -= umBloco;
  }
  caixa.addEventListener('scroll', function () {
    reenquadra();
    agenda();
  }, { passive: true });

  /* --- laterais desfocadas ---------------------------------------------- */
  /* quanto mais perto da borda, mais desfocado e mais apagado o cartao;
     como isso e recalculado a cada quadro, o efeito corre junto do arrasto */
  var LARGURA = 1512;          /* largura do palco */
  var ZONA    = 430;           /* faixa, em px de projeto, onde o efeito age */
  var MAX     = 12;            /* desfoque maximo, em px */
  var cartoes = Array.prototype.slice.call(trilho.children);
  var pedido  = 0;

  function pinta() {
    pedido = 0;
    var rolagem = caixa.scrollLeft;
    for (var i = 0; i < cartoes.length; i++) {
      var c = cartoes[i];
      var meio = c.offsetLeft + c.offsetWidth / 2 - rolagem;
      var borda = Math.min(meio, LARGURA - meio);
      var t = borda >= ZONA ? 0 : (borda <= 0 ? 1 : (ZONA - borda) / ZONA);
      t = t * t;                                   /* comeca suave */
      c.style.setProperty('--desfoque', (t * MAX).toFixed(2) + 'px');
      c.style.setProperty('--esmaece', (1 - t * 0.55).toFixed(3));
    }
  }

  function agenda() {
    if (pedido) return;
    pedido = window.requestAnimationFrame ? requestAnimationFrame(pinta) : setTimeout(pinta, 16);
  }

  /* --- arrastar com o ponteiro ------------------------------------------ */
  /* o palco inteiro é escalado, então o deslocamento do ponteiro precisa ser
     convertido de pixels de tela para pixels do projeto */
  var arrastando = false, x0 = 0, s0 = 0, moveu = 0;

  function escala() {
    return caixa.getBoundingClientRect().width / 1512 || 1;
  }

  caixa.addEventListener('pointerdown', function (e) {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    arrastando = true; moveu = 0;
    x0 = e.clientX; s0 = caixa.scrollLeft;
    caixa.classList.add('arrastando');
    caixa.setPointerCapture(e.pointerId);
  });

  caixa.addEventListener('pointermove', function (e) {
    if (!arrastando) return;
    var d = (e.clientX - x0) / escala();
    moveu = Math.max(moveu, Math.abs(d));
    caixa.scrollLeft = s0 - d;
    if (e.pointerType === 'mouse') e.preventDefault();
  });

  function solta(e) {
    if (!arrastando) return;
    arrastando = false;
    caixa.classList.remove('arrastando');
    try { caixa.releasePointerCapture(e.pointerId); } catch (_) {}
  }
  caixa.addEventListener('pointerup', solta);
  caixa.addEventListener('pointercancel', solta);
  /* um arrasto não deve virar clique num link/foto */
  caixa.addEventListener('click', function (e) {
    if (moveu > 6) { e.preventDefault(); e.stopPropagation(); }
  }, true);

  /* --- roda do mouse: rolagem vertical vira horizontal ------------------- */
  caixa.addEventListener('wheel', function (e) {
    if (Math.abs(e.deltaY) <= Math.abs(e.deltaX)) return;
    caixa.scrollLeft += e.deltaY;
    e.preventDefault();
  }, { passive: false });

  /* --- teclado ---------------------------------------------------------- */
  caixa.tabIndex = 0;
  caixa.addEventListener('keydown', function (e) {
    var passo = 447;   /* largura do cartão + intervalo */
    if (e.key === 'ArrowRight') { caixa.scrollLeft += passo; e.preventDefault(); }
    if (e.key === 'ArrowLeft')  { caixa.scrollLeft -= passo; e.preventDefault(); }
  });

  centraliza();
  window.addEventListener('resize', function () { medir(); agenda(); }, { passive: true });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () {
    ajustaTextos();
    centraliza();
  });
})();
