/* ==========================================================================
   Menu: resposta ao clique.

   O item afunda e volta, com um risco laranja passando por baixo. A troca de
   página espera a animação terminar — sem isso ela nem chegaria a aparecer,
   porque o navegador já teria saído da página.

   Clique com Ctrl/Cmd/Shift, com o botão do meio ou em outra aba não é
   segurado: nesses casos o navegador faz o que sempre faz.
   ========================================================================== */
(function () {
  'use strict';

  var DURACAO = 280;   /* ms — um pouco mais que a animação, para ela fechar */
  var parado = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function anima(el) {
    el.classList.remove('clicou');
    void el.offsetWidth;              /* reinicia a animação a cada clique */
    el.classList.add('clicou');
  }

  Array.prototype.forEach.call(document.querySelectorAll('.nav-link, .nav-botao'), function (a) {
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
