/* ==========================================================================
   "Empresas do grupo" — troca o nome pelo logo quando o arquivo existe.

   A moldura nasce com o nome da empresa; o logo só entra depois de carregar.
   Feito nessa ordem de propósito: se o arquivo faltar, o que fica é o nome,
   e não um ícone de imagem quebrada.
   ========================================================================== */
(function () {
  'use strict';
  Array.prototype.forEach.call(document.querySelectorAll('.empresa img'), function (img) {
    function entrou() { img.parentNode.classList.add('com-logo'); }
    if (img.complete) { if (img.naturalWidth) entrou(); }
    else img.addEventListener('load', entrou);
  });
})();
