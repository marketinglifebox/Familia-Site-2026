/* ==========================================================================
   "Nossos pilares" — as quatro pílulas são botões.

   Sem seleção as quatro ficam idênticas. Ao clicar, a escolhida cresce,
   inverte o lado (rótulo à esquerda, canto arredondado embaixo à direita)
   e recebe o degradê; a foto do círculo grande troca com um cruzamento
   suave. Clicar de novo na mesma volta ao estado neutro.
   ========================================================================== */
(function () {
  'use strict';

  /* Foto do círculo grande para cada pilar.
     AMBIENTE usa a foto do documento original; as outras três ficam com ela
     até chegarem os arquivos definitivos — basta trocar o caminho aqui. */
  var FOTOS = {
    padrao:      'assets/img/pilar-main.jpg',
    ambiente:    'assets/img/pilar-main.jpg',
    agilidade:   'assets/img/pilar-main.jpg',
    produto:     'assets/img/pilar-main.jpg',
    atendimento: 'assets/img/pilar-main.jpg'
  };

  var pilares = Array.prototype.slice.call(document.querySelectorAll('.pilar'));
  var camadaA = document.getElementById('pilarFotoA');
  var camadaB = document.getElementById('pilarFotoB');
  if (!pilares.length || !camadaA || !camadaB) return;

  var frente = camadaA;   /* camada visível no momento */
  var atual = null;

  function trocaFoto(src) {
    if (frente.getAttribute('src') === src) return;
    var fundo = (frente === camadaA) ? camadaB : camadaA;
    fundo.setAttribute('src', src);
    /* deixa o navegador aplicar o src antes de cruzar as camadas */
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        fundo.classList.remove('oculta');
        frente.classList.add('oculta');
        frente = fundo;
      });
    });
  }

  function seleciona(botao) {
    atual = botao;
    pilares.forEach(function (p) {
      p.setAttribute('aria-pressed', String(p === botao));
    });
    trocaFoto(botao ? (FOTOS[botao.dataset.pilar] || FOTOS.padrao) : FOTOS.padrao);
  }

  pilares.forEach(function (p) {
    p.addEventListener('click', function () {
      seleciona(atual === p ? null : p);
    });
  });
})();
