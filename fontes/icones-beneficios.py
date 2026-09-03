# -*- coding: utf-8 -*-
"""Desenha os icones dos beneficios que ainda nao tem foto.

Cada arquivo sai com 342x216 - exatamente o quadro .benef-foto -, fundo creme
#FDF6EE e o traco laranja #E86532 da casa, na mesma linguagem dos icones de
habitos. O desenho fica num quadrado de 140x140 centralizado: qualquer canto
arredondado do cartao (raio maximo 170px) passa longe dele.
"""
import os

LARG, ALT, LADO = 342, 216, 140
DX, DY = (LARG - LADO) / 2.0, (ALT - LADO) / 2.0
# o quadro do icone leva um creme um tom mais quente que o fundo da secao
# (#FDF6EE): sem isso o canto arredondado do cartao sumiria contra a secao
CREME, TINTA = '#F7E7DB', '#E86532'

MOLDE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-hidden="true">
  <rect width="%d" height="%d" fill="%s"/>
  <g transform="translate(%s,%s)" fill="none" stroke="%s" stroke-width="6"
     stroke-linecap="round" stroke-linejoin="round">
%%s
  </g>
</svg>
''' % (LARG, ALT, LARG, ALT, LARG, ALT, CREME, DX, DY, TINTA)

ICONES = {
 # SUBSIDIOS totalpass - halter
 'totalpass': '''
    <path d="M40 70 H100"/>
    <path d="M36 52 V88"/><path d="M104 52 V88"/>
    <rect x="16" y="46" width="14" height="48" rx="6"/>
    <rect x="110" y="46" width="14" height="48" rx="6"/>''',

 # SUBSIDIOS para cursos - capelo
 'cursos': '''
    <path d="M70 26 L124 52 L70 78 L16 52 Z"/>
    <path d="M42 64 V88 C42 100 55 108 70 108 C85 108 98 100 98 88 V64"/>
    <path d="M124 52 V84"/>
    <circle cx="124" cy="90" r="6"/>''',

 # AUXILIO funeral - maos amparando um coracao
 'funeral': '''
    <path d="M70 74 C58 63 46 56 46 44 C46 36 52 30 60 30 C64 30 68 32 70 36
             C72 32 76 30 80 30 C88 30 94 36 94 44 C94 56 82 63 70 74 Z"/>
    <path d="M22 82 C22 106 43 122 70 122 C97 122 118 106 118 82"/>
    <path d="M22 82 L12 68"/><path d="M118 82 L128 68"/>''',

 # SUBSIDIO plano odontologico - dente
 'odonto': '''
    <path d="M70 30 C58 22 34 22 28 42 C22 64 34 76 38 96 C41 110 42 120 50 120
             C58 120 58 106 60 94 C62 83 64 78 70 78 C76 78 78 83 80 94
             C82 106 82 120 90 120 C98 120 99 110 102 96 C106 76 118 64 112 42
             C106 22 82 22 70 30 Z"/>
    <path d="M45 46 C49 38 56 35 63 36"/>''',

 # ATE 3 FREELAS por mes - pessoa a mais
 'freela': '''
    <circle cx="58" cy="48" r="18"/>
    <path d="M24 114 C24 92 39 80 58 80 C77 80 92 92 92 114"/>
    <path d="M100 44 H126"/><path d="M113 31 V57"/>''',

 # ASSIDUIDADE - calendario com visto
 'assiduidade': '''
    <rect x="18" y="32" width="104" height="92" rx="12"/>
    <path d="M18 58 H122"/>
    <path d="M44 20 V44"/><path d="M96 20 V44"/>
    <path d="M50 88 L64 102 L92 72"/>''',

 # SUBSIDIO plano de saude - coracao com o traco do batimento
 'saude': '''
    <path d="M70 120 C40 99 22 84 22 60 C22 44 34 33 48 33 C58 33 66 38 70 46
             C74 38 82 33 92 33 C106 33 118 44 118 60 C118 84 100 99 70 120 Z"/>
    <path d="M30 68 H50 L58 50 L70 86 L78 64 H110"/>''',

 # PREMIACOES financeiras por desempenho - trofeu
 'premiacoes': '''
    <path d="M44 24 H96 V50 C96 68 84 80 70 80 C56 80 44 68 44 50 Z"/>
    <path d="M44 32 H30 C30 50 37 58 46 60"/>
    <path d="M96 32 H110 C110 50 103 58 94 60"/>
    <path d="M70 80 V96"/>
    <path d="M50 118 L55 96 H85 L90 118 Z"/>
    <path d="M70 34 L74.7 43.5 L85.2 45 L77.6 52.4 L79.4 62.9 L70 58 L60.6 62.9
             L62.4 52.4 L54.8 45 L65.3 43.5 Z" stroke-width="5"/>''',

 # VALE transporte - onibus
 'transporte': '''
    <rect x="18" y="26" width="104" height="82" rx="14"/>
    <rect x="32" y="40" width="76" height="30" rx="6"/>
    <path d="M70 40 V70"/>
    <path d="M18 84 H122"/>
    <path d="M34 96 H42"/><path d="M98 96 H106"/>
    <circle cx="42" cy="116" r="9"/><circle cx="98" cy="116" r="9"/>''',

 # SEGURO de vida - escudo com coracao
 'seguro': '''
    <path d="M70 20 L118 38 V70 C118 98 96 116 70 126 C44 116 22 98 22 70 V38 Z"/>
    <path d="M70 98 C56 88 46 80 46 70 C46 62 52 57 59 57 C64 57 68 60 70 64
             C72 60 76 57 81 57 C88 57 94 62 94 70 C94 80 84 88 70 98 Z"/>''',

 # CESTA de natalidade - carrinho de bebe
 'natalidade': '''
    <path d="M34 72 A36 36 0 0 1 106 72"/>
    <path d="M70 36 V72"/>
    <path d="M22 72 H118"/>
    <path d="M34 72 C34 94 50 104 70 104 C90 104 106 94 106 72"/>
    <path d="M106 72 C122 68 128 58 126 48"/>
    <path d="M54 103 L46 112"/><path d="M86 103 L94 112"/>
    <circle cx="42" cy="118" r="8"/><circle cx="98" cy="118" r="8"/>''',

 # AGENDA GERAL lifebox - planner com marcador
 'agenda': '''
    <rect x="28" y="24" width="90" height="102" rx="10"/>
    <path d="M28 44 H14"/><path d="M28 68 H14"/><path d="M28 92 H14"/>
    <path d="M46 62 H84"/><path d="M46 82 H84"/><path d="M46 102 H72"/>
    <path d="M98 24 V56 L90 47 L82 56 V24"/>''',
}

DESTINO = 'assets/svg/beneficios/'
for nome, desenho in ICONES.items():
    with open(DESTINO + nome + '.svg', 'w') as f:
        f.write(MOLDE % desenho.rstrip('\n'))
    print('escrito', DESTINO + nome + '.svg')
