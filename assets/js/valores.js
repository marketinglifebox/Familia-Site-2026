/* ==========================================================================
   "Nossos valores" — carrossel contínuo, o mesmo da página inicial.
   O mecanismo está em carrossel.js; aqui só o enquadramento do documento.
   ========================================================================== */
(function () {
  'use strict';
  var caixa  = document.getElementById('valorCarrossel');
  var trilho = document.getElementById('valorTrilho');
  if (!caixa || !trilho || !window.Carrossel) return;

  /* em repouso a fileira fica como no documento: o primeiro cartão inteiro
     começa em x=416 e o anterior aparece cortado pela moldura */
  var c = window.Carrossel(caixa, trilho, { recuo: 364, passo: 780, modo: 'fora', desfoque: 9, esmaece: 0 });
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(c.centraliza);
})();
