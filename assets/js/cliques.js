/* ==========================================================================
   Cliques com resposta.

   Vale para os itens do menu e para os atalhos de "No Lifebox acreditamos em"
   (a marca e o botão logo abaixo dela). O elemento afunda e volta; nos itens
   do menu um risco laranja passa por baixo, e na marca ela dá um pulinho.

   Elementos com o mesmo `data-toque` reagem juntos: clicar na marca anima
   também o botão, e vice-versa — os dois levam ao mesmo lugar.

   A troca de página espera a animação terminar. Sem isso ela nem chegaria a
   aparecer, porque o navegador já teria saído da página. Clique com
   Ctrl/Cmd/Shift, com o botão do meio ou com movimento reduzido ligado não é
   segurado: nesses casos o navegador faz o que sempre faz.
   ========================================================================== */
(function () {
  'use strict';

  var SELETOR = '.nav-link, .nav-botao, .marca-link, .pilha-botao';
  var DURACAO = 320;   /* ms — um pouco mais que a mais longa das animações */
  var parado = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function grupoDe(el) {
    var g = el.getAttribute('data-toque');
    return g ? document.querySelectorAll('[data-toque="' + g + '"]') : [el];
  }

  function anima(el) {
    Array.prototype.forEach.call(grupoDe(el), function (a) {
      a.classList.remove('clicou');
      void a.offsetWidth;             /* reinicia a animação a cada clique */
      a.classList.add('clicou');
    });
  }

  Array.prototype.forEach.call(document.querySelectorAll(SELETOR), function (a) {
    a.addEventListener('animationend', function () { a.classList.remove('clicou'); });

    a.addEventListener('click', function (e) {
      if (e.metaKey || e.ctrlKey || e.shiftKey || e.altKey || e.button !== 0) return;
      anima(a);

      var destino = a.getAttribute('href') || '';
      /* item da própria página: só a animação, não há para onde ir */
      if (a.getAttribute('aria-current') === 'page') { e.preventDefault(); return; }
      if (!destino) return;
      if (parado) return;                 /* movimento desligado: vai direto */

      e.preventDefault();
      setTimeout(function () { window.location.href = destino; }, DURACAO);
    });
  });
})();
