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

  var umBloco = 0;
  function medir() {
    umBloco = trilho.scrollWidth / 3;
  }

  /* posição inicial: bloco do meio, com um cartão assomando à esquerda,
     como no documento */
  function centraliza() {
    medir();
    caixa.scrollLeft = umBloco - 124;
  }

  function reenquadra() {
    if (!umBloco) return;
    if (caixa.scrollLeft < umBloco * 0.5)      caixa.scrollLeft += umBloco;
    else if (caixa.scrollLeft > umBloco * 1.5) caixa.scrollLeft -= umBloco;
  }
  caixa.addEventListener('scroll', reenquadra, { passive: true });

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
  window.addEventListener('resize', function () { medir(); }, { passive: true });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(centraliza);
})();
