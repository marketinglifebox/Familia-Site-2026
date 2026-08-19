/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./index.html', './quem-somos.html', './assets/js/**/*.js'],
  theme: {
    extend: {
      colors: {
        /* ---- Paleta extraida do PDF original ---- */
        cream:        '#FDF6EF', // fundo geral
        orange:       '#E86532', // laranja da marca
        'orange-lt':  '#EB7C25', // fim do gradiente da pilula "AGILIDADE"
        'green-band': '#489A54', // faixas "TRABALHE CONOSCO"
        'green-line': '#64A568', // curvas decorativas
        'green-head': '#159345', // titulo "POR QUE"
        navy:         '#00358E', // links do menu
        'logo-dark':  '#0D1B2A', // wordmark LIFEBOX
        salmon:       '#EE9E77', // palavra "FAMILIA" do logo
        ink:          '#000000', // textos pretos
        'ink-soft':   '#1C1C1C', // rodape / copyright
      },
      fontFamily: {
        geo:  ['Poppins', 'system-ui', 'sans-serif'],          // sans geometrica
        cond: ['"Fira Sans Condensed"', 'Impact', 'sans-serif'], // sans condensada pesada
      },
    },
  },
  plugins: [],
}
