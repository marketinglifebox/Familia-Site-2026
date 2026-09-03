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
     Os sete hábitos, com o texto do material do cliente. Cada símbolo já
     existente foi correlacionado ao hábito que ele desenha: a cabeça com o
     alvo para o objetivo em mente, as mãos erguendo a medalha para o que vem
     primeiro, o cérebro para o pensamento, as mãos em coração para o cuidado
     consigo. As aspas são do próprio material.                             */
  var HABITOS = {
    proatividade: {
      titulo: 'PROATIVIDADE',
      texto: '“Eu sou o autor da minha vida. Sou responsável pelas minhas escolhas e ações, independente das circunstâncias externas”'
    },
    foco: {
      titulo: 'COMECE COM OBJETIVO EM MENTE',
      texto: '“Eu vejo o destino antes de começar a jornada tendo clareza sobre os objetivos e propósito antes de agir.”'
    },
    atendimento: {
      titulo: 'COMPREENDER PRIMEIRO PARA DEPOIS SER COMPREENDIDO',
      texto: '“Eu ouço para entender, não para responder. Mantenho abertura para diferentes pontos de vistas e experiências.”'
    },
    excelencia: {
      titulo: 'PRIMEIRO O MAIS IMPORTANTE',
      texto: '“A prioridade guia minhas ações. Priorização conforme objetivos e valores pessoais. Tarefas importantes acima das urgentes.”'
    },
    colaboracao: {
      titulo: 'SINERGIA',
      texto: '“Juntos somos mais fortes.”'
    },
    mentalidade: {
      titulo: 'PENSAMENTO GANHA-GANHA',
      texto: '“Eu próspero ao criar valor para todos, colaboração onde todos podem sair beneficiados.”'
    },
    cuidado: {
      titulo: 'AFINE O INSTRUMENTO',
      texto: '“Cuidar de mim (físico, emocional, mental e espiritual) é meu maior investimento a fim de fazer o equilíbrio e a eficácia a longo prazo.”'
    }
  };

  /* corpos possíveis do título, do tamanho do documento para baixo: o maior
     que couber na altura reservada é o que vale */
  var CORPOS = [96.68, 82, 70, 60, 52, 46];
  var TETO_TITULO = 210;   /* px de altura para o título, acima do parágrafo */

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

  /* o maior corpo em que o título ainda cabe na altura reservada */
  function ajustaTitulo() {
    for (var i = 0; i < CORPOS.length; i++) {
      titulo.style.fontSize = CORPOS[i] + 'px';
      if (titulo.offsetHeight <= TETO_TITULO || i === CORPOS.length - 1) return;
    }
  }

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
    ajustaTitulo();
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
