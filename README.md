# Família Lifebox — 2026

Réplica **pixel-perfect** em HTML5 + Tailwind CSS + JavaScript da página
`pagina_1.pdf` (landing page "Família Lifebox / Trabalhe Conosco").

O objetivo do projeto é fidelidade visual absoluta ao documento original:
posições, proporções, cores, tipografia e espaçamentos foram extraídos
diretamente do PDF e reproduzidos em coordenadas exatas.

---

## Como executar

Basta abrir `index.html` no navegador — o site é estático e todos os
recursos (fontes, imagens, SVGs, CSS) são locais, sem dependência de CDN.

Opcionalmente, com um servidor local:

```bash
npm install     # apenas para recompilar o CSS
npm run serve   # http://localhost:3000
```

Para recompilar o Tailwind depois de editar `index.html` ou `src/input.css`:

```bash
npm run build   # gera assets/css/tailwind.css
npm run dev     # modo watch
```

---

## Arquitetura

### Palco de escala fixa (fidelidade de proporção)

O documento original é uma prancha de **1512 × 5577 px**. Todos os elementos
são posicionados em coordenadas absolutas dessa prancha, dentro de `.stage`.

`assets/js/main.js` calcula `k = larguraDaViewport / 1512` e aplica
`transform: scale(k)` no palco, ajustando a altura do contêiner. Assim a
página se adapta a qualquer largura de tela **sem alterar uma única
proporção, alinhamento ou espaçamento** do design original — que é
exatamente a exigência de fidelidade do briefing.

Sem JavaScript há um fallback em CSS puro (`zoom: calc(100vw / 1512)`).

### Estrutura de pastas

```
index.html                 marcação completa da página
src/input.css              fonte do Tailwind + @font-face + componentes
tailwind.config.js         paleta e famílias tipográficas do projeto
assets/css/tailwind.css    CSS compilado (gerado por `npm run build`)
assets/js/main.js          escala proporcional do palco
assets/fonts/*.woff2       fontes auto-hospedadas (latin + latin-ext)
assets/img/*.jpg           fotografias extraídas do PDF
assets/img/grain-orange.png textura granulada da faixa "Empresas do Grupo"
assets/svg/*.svg           artes vetoriais traçadas a partir do PDF
```

---

## Paleta extraída do PDF

| Token          | Hex       | Uso                                        |
|----------------|-----------|--------------------------------------------|
| `cream`        | `#FDF6EF` | fundo geral, textos sobre laranja          |
| `orange`       | `#E86532` | cor institucional (faixas, botões, títulos)|
| `orange-lt`    | `#EB7C25` | final do gradiente da pílula "AGILIDADE"   |
| `green-band`   | `#489A54` | faixas "TRABALHE CONOSCO"                  |
| `green-line`   | `#64A568` | curvas decorativas                         |
| `green-head`   | `#159345` | título "POR QUE"                           |
| `navy`         | `#00358E` | links do menu                              |
| `logo-dark`    | `#0D1B2A` | wordmark "LIFEBOX"                         |
| `salmon`       | `#EE9E77` | palavra "FAMÍLIA" do logotipo              |
| `ink`          | `#000000` | textos pretos                              |
| `ink-soft`     | `#1C1C1C` | rodapé / copyright                         |

---

## Tipografia

O PDF é um arquivo **rasterizado** (a página inteira é composta por imagens
JPEG recortadas — não há texto vetorial nem fontes embutidas). As famílias
foram, portanto, identificadas por engenharia reversa: medição da altura de
caixa alta, da largura de cada palavra e comparação de forma (IoU) contra
dezenas de candidatas.

| Papel no design            | Fonte aplicada           | Observação                                    |
|----------------------------|--------------------------|-----------------------------------------------|
| Sans geométrica (larga)    | **Poppins** 300/400/500/600 | "POR QUE", pílulas, Missão/Visão/Valores, logo |
| Sans condensada            | **Fira Sans Condensed** 400–800 | menu, títulos de seção, benefícios, rodapé |

Cada bloco de texto tem `font-size` derivado da altura de caixa alta medida
no PDF e `letter-spacing` calculado para reproduzir **exatamente** a largura
original de cada palavra. O posicionamento vertical usa `line-height: 1` com
o `top` compensado pelas métricas reais da fonte (ascender/cap-height), de
modo que o topo das maiúsculas caia no pixel correto.

> As fontes originais do documento são proprietárias e não puderam ser
> identificadas com certeza absoluta; Poppins e Fira Sans Condensed são as
> equivalentes de web font mais próximas disponíveis (Google Fonts),
> auto-hospedadas para funcionamento offline e renderização estável.

---

## Artes vetoriais

Elementos que no PDF são apenas pixels foram **vetorizados** (potrace) para
permanecerem nítidos em qualquer escala:

- `ser-um-lifer.svg` — lettering "SER UM LIFER?" (inclui o "E" em épsilon,
  característica da fonte display original, impossível de reproduzir com
  web fonts);
- `logo-lifebox.svg`, `logo-mark.svg` — wordmark e símbolo da marca;
- `mark-missao/visao/valores.svg` — os três selos da seção institucional;
- `wave.svg` — a onda que abre o bloco laranja (traçada ponto a ponto a
  partir da fronteira real da forma no PDF);
- `curves-benef.svg`, `curves-footer.svg` — as curvas verdes decorativas.

As fotografias foram recortadas do PDF na resolução máxima disponível.

---

## JavaScript

O uso de JS é mínimo e restrito ao que o documento exige:

1. **Escala proporcional do palco** (`assets/js/main.js`).
2. **Faixas "TRABALHE CONOSCO"** — o padrão de texto repetido em faixa é uma
   marquise; ela desliza continuamente respeitando o passo real do design
   (ciclo de 398 px). O movimento é desativado automaticamente sob
   `prefers-reduced-motion: reduce`, quando a faixa volta ao quadro estático
   idêntico ao do PDF.

Nenhuma outra interação, animação ou liberdade de usabilidade foi adicionada.

---

## Verificação de fidelidade

A página foi renderizada em 1512 px e comparada pixel a pixel com o PDF
rasterizado na mesma escala. A diferença média absoluta ficou em
**≈ 12,8 / 765** (≈ 1,7 %), concentrada apenas em:

- diferenças de desenho de glifo entre as fontes originais (proprietárias) e
  as substitutas de web font;
- reencode JPEG das fotografias;
- o granulado aleatório da faixa "Empresas do Grupo" (estatística idêntica,
  ruído necessariamente distinto).

Regiões de foto e de cor chapada apresentam diferença ≈ 0–3.

---

## Observação sobre conteúdo parcialmente visível

Os benefícios das pontas do carrossel aparecem cortados no documento
original. O primeiro (à esquerda) e o último (à direita) foram completados
como **"SUBSÍDIO / gympass"** e **"FOLGA / no aniversário"** — os trechos
visíveis no PDF ("…ÍDIO / …pass" e "FO… / no a…") são compatíveis com essa
leitura. As larguras e posições dos fragmentos visíveis foram calibradas
para coincidir com o original.
