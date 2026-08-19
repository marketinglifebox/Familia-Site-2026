/* ==========================================================================
   "Nossos hábitos" — bolhas flutuantes + aba que abre em círculo.

   Ao clicar numa bolha:
     1. o círculo creme cresce a partir do ponto exato da bolha clicada;
     2. a bolha escolhida viaja para o topo da aba e vira o ícone do painel;
     3. as outras seis reorganizam-se nas posições do layout aberto;
     4. o bloco de título encolhe para a coluna da esquerda.
   ========================================================================== */
(function () {
  'use strict';

  /* ---- Conteúdo dos hábitos -------------------------------------------
     PROATIVIDADE foi transcrito do PDF. Os demais textos são provisórios —
     basta substituir titulo/texto abaixo pelos definitivos.               */
  var HABITOS = {
    atendimento: {
      titulo: 'ATENDIMENTO',
      texto: 'Eu sirvo com atenção genuína. Cada pessoa que entra na Lifebox merece ser vista, ouvida e bem cuidada do começo ao fim.'
    },
    excelencia: {
      titulo: 'EXCELÊNCIA',
      texto: 'Eu entrego o meu melhor em cada detalhe. Faço bem feito na primeira vez e não me acostumo com o suficiente.'
    },
    colaboracao: {
      titulo: 'COLABORAÇÃO',
      texto: 'Eu construo junto. Compartilho o que sei, peço ajuda quando preciso e celebro o resultado como time.'
    },
    proatividade: {
      titulo: 'PROATIVIDADE',
      texto: 'Eu sou autor da minha vida. Sou responsável pelas minhas escolhas e ações independentes das circunstâncias externas.'
    },
    mentalidade: {
      titulo: 'MENTALIDADE DE DONO',
      texto: 'Eu cuido do negócio como se fosse meu. Penso no todo, zelo pelos recursos e assumo o resultado das minhas decisões.'
    },
    foco: {
      titulo: 'FOCO EM RESULTADO',
      texto: 'Eu sei aonde quero chegar. Priorizo o que gera valor, acompanho os números e transformo esforço em resultado.'
    },
    cuidado: {
      titulo: 'CUIDADO',
      texto: 'Eu trato as pessoas com respeito e empatia. Cuido de quem está ao meu lado e do ambiente que construímos juntos.'
    }
  };

  /* ---- Layout aberto: 6 vagas medidas no PDF da aba (centro x, y, diâmetro) */
  var VAGAS = {
    A: { cx: 186.5, cy: 220.5,  d: 190 },
    B: { cx: 626,   cy: 250,    d: 153 },
    C: { cx: 410,   cy: 412,    d: 173 },
    D: { cx: 416.5, cy: 905.5,  d: 262 },
    E: { cx: 677,   cy: 1104,   d: 191 },
    F: { cx: 155,   cy: 1152,   d: 191 }
  };
  /* ordem em que as bolhas restantes ocupam as vagas (reproduz o PDF) */
  var ORDEM = ['B', 'A', 'C', 'F', 'E', 'D'];

  /* ---- Vaga do ícone dentro do painel ---------------------------------- */
  var PAINEL_ICONE = { cx: 1370.5, cy: 140, d: 200 };  /* 200 * 0.72 = 144px de ícone */

  var secao   = document.getElementById('habitosSecao');
  var painel  = document.getElementById('painel');
  var icone   = document.getElementById('painelIcone');
  var titulo  = document.getElementById('painelTitulo');
  var texto   = document.getElementById('painelTexto');
  if (!secao || !painel) return;

  var bolhas = Array.prototype.slice.call(secao.querySelectorAll('.bolha'));
  var aberta = null;

  /* geometria original de cada bolha, lida do próprio CSS inline */
  bolhas.forEach(function (b) {
    b.dataset.cx = parseFloat(b.style.left) + parseFloat(b.style.width) / 2;
    b.dataset.cy = parseFloat(b.style.top) + parseFloat(b.style.height) / 2;
    b.dataset.d  = parseFloat(b.style.width);
    b.setAttribute('aria-expanded', 'false');
  });

  function mover(b, alvo) {
    var s  = alvo.d / (+b.dataset.d);
    var dx = alvo.cx - (+b.dataset.cx);
    var dy = alvo.cy - (+b.dataset.cy);
    b.style.transform = 'translate(' + dx + 'px,' + dy + 'px) scale(' + s + ')';
  }

  function fechar() {
    secao.classList.remove('aberto');
    bolhas.forEach(function (b) {
      b.style.transform = '';
      b.style.zIndex = '';
      b.setAttribute('aria-expanded', 'false');
    });
    aberta = null;
  }

  function abrir(b) {
    var id = b.dataset.id;
    var dados = HABITOS[id];
    if (!dados) return;

    /* origem do crescimento do círculo = centro da bolha clicada */
    var px = ((+b.dataset.cx) - painel.offsetLeft) / painel.offsetWidth * 100;
    var py = ((+b.dataset.cy) - painel.offsetTop) / painel.offsetHeight * 100;
    painel.style.setProperty('--ox', px + '%');
    painel.style.setProperty('--oy', py + '%');

    /* conteúdo */
    icone.src = b.querySelector('img').getAttribute('src');
    icone.alt = dados.titulo;
    titulo.textContent = dados.titulo;
    texto.innerHTML = '<p>' + dados.texto + '</p>';

    /* posições */
    var i = 0;
    bolhas.forEach(function (outra) {
      if (outra === b) {
        outra.style.zIndex = '4';
        mover(outra, PAINEL_ICONE);
      } else {
        outra.style.zIndex = '';
        mover(outra, VAGAS[ORDEM[i++]]);
      }
      outra.setAttribute('aria-expanded', String(outra === b));
    });

    secao.classList.add('aberto');
    aberta = b;
  }

  bolhas.forEach(function (b) {
    b.addEventListener('click', function (e) {
      e.stopPropagation();
      if (aberta === b) fechar(); else abrir(b);
    });
  });

  /* clicar fora da aba (na área laranja) fecha */
  secao.addEventListener('click', function () { if (aberta) fechar(); });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape' && aberta) fechar();
  });
})();
