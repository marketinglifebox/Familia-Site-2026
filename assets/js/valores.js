/* ==========================================================================
   "Nossos valores" — carrossel contínuo, o mesmo da página inicial.
   O mecanismo está em carrossel.js; aqui só o enquadramento do documento.
   ========================================================================== */
(function () {
  'use strict';
  var caixa  = document.getElementById('valorCarrossel');
  var trilho = document.getElementById('valorTrilho');
  if (!caixa || !trilho || !window.Carrossel) return;

  /* parado, a fileira começa com o primeiro cartão à esquerda e os seguintes
     saindo pela moldura, para ficar claro que ela corre */
  var c = window.Carrossel(caixa, trilho, { recuo: -416, passo: 780, modo: 'fora', desfoque: 6, esmaece: 0.25 });

  /* ícone ainda não entregue: o quadro recebe a marca da casa em vez do ícone
     de imagem quebrada. Depois da triplicação, para alcançar também as cópias */
  Array.prototype.forEach.call(trilho.querySelectorAll('.valor-icone img'), function (img) {
    function falta() { img.parentNode.classList.add('sem-icone'); }
    img.addEventListener('error', falta);
    if (img.complete && !img.naturalWidth) falta();
  });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(c.centraliza);
})();
