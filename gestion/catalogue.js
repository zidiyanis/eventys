/* Eventys — catalogue partagé par l'app de gestion (/gestion), la page client
   (/reserver) et le flux calendrier (/api/calendrier).
   Pour changer un prix ou un stock de ces trois endroits : c'est ici.
   (Le site vitrine garde sa propre liste dans assets/js/donnees.js.)
   Nappes absentes pour l'instant : Yanis étudie la revente. */
(function (root) {
  var CAT = {
    hiverChaise: 2, // prix de la chaise quand le tarif hiver est activé dans les réglages
    items: [
      { k: 'chaise',    n: 'Chaise Napoléon blanche',       c: 'chaise', cp: 'chaises',               s: 'la pièce',                     p: 3,  stock: 100,  img: 'chaise-rang-900.webp' },
      { k: 'ronde',     n: 'Table ronde Ø120 cm',           c: 'table ronde', cp: 'tables rondes',    s: '8 à 10 personnes',             p: 10, stock: 8,    img: 'table-ronde-sauge-dessus-900.webp' },
      { k: 'rect',      n: 'Table rectangulaire 70×180 cm', c: 'table rect.', cp: 'tables rect.',     s: '8 à 10 personnes',             p: 10, stock: 10,   img: 'table-rect-fuchsia-900.webp' },
      { k: 'mange',     n: 'Mange-debout 80×110 cm',        c: 'mange-debout', cp: 'mange-debout',    s: 'pour un cocktail',             p: 7,  stock: null, img: '' },
      { k: 'arche',     n: 'Arche dorée',                   c: 'arche', cp: 'arches',                 s: 'circulaire ou rectangulaire',  p: 40, stock: 2,    img: 'arche-fleurie-900.webp' },
      { k: 'vaisselle', n: 'Kit vaisselle',                 c: 'kit vaisselle', cp: 'kits vaisselle', s: 'verre, couverts, 2 assiettes', p: 2,  stock: 75,   img: 'vaisselle-couvert-complet-900.webp' }
    ]
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = CAT;
  else root.EV_CAT = CAT;
})(typeof self !== 'undefined' ? self : this);
