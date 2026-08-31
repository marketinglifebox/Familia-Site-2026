/* ==========================================================================
   Tela de carregamento.

   Ela já está na página desde a primeira pintura (é o primeiro elemento do
   corpo, e o estilo dela vem na folha que bloqueia a renderização). Aqui só
   fica a saída: some quando a página está de fato inteira — fontes medidas e
   imagens baixadas —, e some de qualquer jeito depois do teto, para que uma
   foto que não chega nunca deixe alguém preso olhando o giro.

   O tempo mínimo evita o pior dos dois mundos: numa página que já está em
   cache, a tela apareceria e sumiria no mesmo quadro, o que se vê como um
   piscar.
   ========================================================================== */
(function () {
  'use strict';

  var tela = document.getElementById('carregando');
  if (!tela) return;

  var MINIMO = 400;    /* ms que ela fica na tela, mesmo se já estiver pronta */
  var TETO   = 6000;   /* ms: some de qualquer jeito */
  var SAIDA  = 420;    /* ms do esmaecer (igual ao CSS) */
  var inicio = Date.now();
  var saiu   = false;

  function some() {
    if (saiu) return;
    saiu = true;
    setTimeout(function () {
      tela.classList.add('saiu');
      setTimeout(function () {
        if (tela.parentNode) tela.parentNode.removeChild(tela);
      }, SAIDA);
    }, Math.max(0, MINIMO - (Date.now() - inicio)));
  }

  /* pronto = fontes medidas E imagens baixadas */
  var faltam = 2;
  function marca() { if (--faltam <= 0) some(); }

  if (document.fonts && document.fonts.ready) document.fonts.ready.then(marca, marca);
  else marca();

  if (document.readyState === 'complete') marca();
  else window.addEventListener('load', marca);

  setTimeout(some, TETO);
})();
