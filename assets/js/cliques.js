/* ==========================================================================
   Cliques com resposta.

   Vale para os itens do menu e para os atalhos de "No Lifebox acreditamos em"
   (a marca e o botão logo abaixo dela). O elemento afunda e volta; nos itens
   do menu um risco laranja passa por baixo, e na marca ela dá um pulinho.

   Elementos com o mesmo `data-toque` reagem juntos: clicar na marca anima
   também o botão, e vice-versa — os dois levam ao mesmo lugar.

   A troca de página espera a animação terminar e sai pela transição de
   transicao.js — a bola que cresce do ponto do clique. Clique com
   Ctrl/Cmd/Shift, com o botão do meio ou com movimento reduzido ligado não é
   segurado: nesses casos o navegador faz o que sempre faz.
   ========================================================================== */
(function () {
  'use strict';

  var SELETOR = '.nav-link, .nav-botao, .marca-link, .pilha-botao, .vaga-botao';
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

      /* âncora da própria página: só o salto, sem a bola da transição - não
         há recarga que a desfaça do outro lado. Tratado sempre aqui, mesmo com
         movimento reduzido, porque o salto nativo rolaria também o .stage-wrap */
      var mesmaPagina = destino.charAt(0) === '#' && document.getElementById(destino.slice(1));
      if (mesmaPagina) {
        e.preventDefault();
        /* scrollTo na janela, e nao scrollIntoView: este ultimo rola também
           os ancestrais roláveis, e o palco vive dentro de um .stage-wrap com
           overflow:hidden — que ele empurraria para o lado */
        var y = mesmaPagina.getBoundingClientRect().top + window.pageYOffset;
        try { window.scrollTo({ top: y, behavior: parado ? 'auto' : 'smooth' }); }
        catch (_) { window.scrollTo(0, y); }
        /* num iframe com sandbox o replaceState levanta SecurityError, e sem o
           try o resto do clique morreria com ele */
        try { if (history.replaceState) history.replaceState(null, '', destino); } catch (_) {}
        return;
      }

      if (parado) {                       /* movimento desligado: vai direto */
        if (window.Roteador && window.Roteador(destino)) e.preventDefault();
        return;
      }

      e.preventDefault();
      var r = a.getBoundingClientRect();
      var px = e.clientX || (r.left + r.width / 2);
      var py = e.clientY || (r.top + r.height / 2);
      /* a previa de arquivo unico troca de palco sem recarregar nada; quando
         ela assume a navegacao, nao ha para onde ir */
      function vai() {
        if (window.Roteador && window.Roteador(destino)) return;
        window.location.href = destino;
      }
      if (window.Transicao) window.Transicao.sai(px, py, vai);
      else setTimeout(vai, DURACAO);
    });
  });
})();
