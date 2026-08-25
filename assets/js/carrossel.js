/* ==========================================================================
   Carrossel contínuo — o mesmo mecanismo usado em "Benefícios Lifebox" e em
   "Nossos valores".

   A fileira corre para os dois lados: arrastando com o mouse, com o dedo, com
   a roda ou pelo teclado. O conteúdo é triplicado e a posição volta ao bloco
   do meio sempre que chega perto de uma ponta, de modo que nunca há fim.

   Perto das bordas cada cartão vai desfocando e esmaecendo, e como isso é
   recalculado a cada quadro da rolagem o efeito acompanha o arrasto.

   Uso:  Carrossel(caixa, trilho, { recuo:124, passo:447 })
   ========================================================================== */
window.Carrossel = function (caixa, trilho, opcoes) {
  'use strict';
  if (!caixa || !trilho) return null;
  opcoes = opcoes || {};

  var LARGURA = 1512;                    /* largura do palco */
  var ZONA    = opcoes.zona || 430;      /* faixa onde o desfoque age */
  var MAX     = opcoes.desfoque == null ? 12 : opcoes.desfoque;   /* desfoque máximo, px */
  var ESMAECE = opcoes.esmaece == null ? 0.55 : opcoes.esmaece;   /* quanto apaga */
  /* 'borda': mede a distância do centro do cartão até a borda do palco.
     'fora' : mede quanto do cartão já saiu do palco - serve para fileiras que
              em repouso já nascem com um cartão cortado pela moldura, como a
              de "Nossos valores", que assim fica igual ao documento parada. */
  var MODO    = opcoes.modo || 'borda';
  var recuo   = opcoes.recuo || 0;       /* enquadramento inicial do documento */
  var passo   = opcoes.passo || 447;     /* salto de uma seta do teclado */

  /* --- triplica os cartões para o laço ---------------------------------- */
  var originais = Array.prototype.slice.call(trilho.children);
  function bloco() {
    var frag = document.createDocumentFragment();
    originais.forEach(function (c) {
      var copia = c.cloneNode(true);
      copia.setAttribute('aria-hidden', 'true');
      Array.prototype.forEach.call(copia.querySelectorAll('img'), function (i) { i.alt = ''; });
      frag.appendChild(copia);          /* mantém a ordem original */
    });
    return frag;
  }
  trilho.insertBefore(bloco(), trilho.firstChild);   /* cópia à esquerda */
  trilho.appendChild(bloco());                       /* cópia à direita  */

  var cartoes = Array.prototype.slice.call(trilho.children);
  var umBloco = 0;
  function medir() {
    /* a distancia entre um cartao e o seu clone tres blocos adiante; usar
       scrollWidth/3 erraria pela metade de um intervalo, porque a fileira tem
       um intervalo a menos que o numero de cartoes */
    umBloco = cartoes[originais.length].offsetLeft - cartoes[0].offsetLeft;
  }

  function centraliza() {
    medir();
    caixa.scrollLeft = umBloco + recuo;
    pinta();
  }

  function reenquadra() {
    if (!umBloco) return;
    if (caixa.scrollLeft < umBloco * 0.5)      caixa.scrollLeft += umBloco;
    else if (caixa.scrollLeft > umBloco * 1.5) caixa.scrollLeft -= umBloco;
  }

  /* --- laterais desfocadas ---------------------------------------------- */
  var pedido = 0;
  function pinta() {
    pedido = 0;
    var rolagem = caixa.scrollLeft;
    for (var i = 0; i < cartoes.length; i++) {
      var c = cartoes[i];
      var esq = c.offsetLeft - rolagem, dir = esq + c.offsetWidth, t;
      if (MODO === 'fora') {
        var fora = Math.max(0, -esq, dir - LARGURA) / c.offsetWidth;
        t = Math.min(1, Math.max(0, (fora - 0.5) / 0.42));
      } else {
        var meio = esq + c.offsetWidth / 2;
        var borda = Math.min(meio, LARGURA - meio);
        t = borda >= ZONA ? 0 : (borda <= 0 ? 1 : (ZONA - borda) / ZONA);
      }
      t = t * t;                                   /* começa suave */
      c.style.setProperty('--desfoque', (t * MAX).toFixed(2) + 'px');
      c.style.setProperty('--esmaece', (1 - t * ESMAECE).toFixed(3));
    }
  }
  function agenda() {
    if (pedido) return;
    pedido = window.requestAnimationFrame ? requestAnimationFrame(pinta) : setTimeout(pinta, 16);
  }

  caixa.addEventListener('scroll', function () { reenquadra(); agenda(); }, { passive: true });

  /* --- arrastar com o ponteiro ------------------------------------------ */
  /* o palco inteiro é escalado, então o deslocamento do ponteiro precisa ser
     convertido de pixels de tela para pixels do projeto */
  var arrastando = false, x0 = 0, s0 = 0, moveu = 0;
  function escala() { return caixa.getBoundingClientRect().width / LARGURA || 1; }

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
    if (e.key === 'ArrowRight') { caixa.scrollLeft += passo; e.preventDefault(); }
    if (e.key === 'ArrowLeft')  { caixa.scrollLeft -= passo; e.preventDefault(); }
  });

  centraliza();
  window.addEventListener('resize', function () { medir(); agenda(); }, { passive: true });

  /* enquanto a fileira está escondida todas as medidas dão zero, e o
     enquadramento de repouso sai errado; guardar a instância permite
     reenquadrá-la assim que ela aparece */
  var api = { centraliza: centraliza, medir: medir, pinta: pinta, cartoes: cartoes, trilho: trilho };
  (window.Carrosseis = window.Carrosseis || []).push(api);
  return api;
};
