/* Eventys — catalogue partagé par l'app de gestion (/gestion), la page client
   (/reserver), le devis (/devis) et le flux calendrier (/api/calendrier).
   Pour changer un prix, un stock ou une photo de ces endroits : c'est ici.
   (Le site vitrine garde sa propre liste dans assets/js/donnees.js.)
   Nappes absentes pour l'instant : Yanis étudie la revente. */
(function (root) {
  var CAT = {
    hiverChaise: 2, // prix de la chaise quand le tarif hiver est activé dans les réglages
    /* Les rubriques de la page client, dans l'ordre d'affichage. */
    cats: [
      { k: 'assises',  n: 'Chaises' },
      { k: 'tables',   n: 'Tables' },
      { k: 'deco',     n: 'Arche et vaisselle' }
    ],
    items: [
      { k: 'chaise',    cat: 'assises', n: 'Chaise Napoléon blanche',       c: 'chaise', cp: 'chaises',               s: 'la pièce',                     p: 3,  stock: 100,  img: 'chaise-terrasse-900.webp' },
      { k: 'ronde',     cat: 'tables',  n: 'Table ronde Ø120 cm',           c: 'table ronde', cp: 'tables rondes',    s: '8 à 10 personnes',             p: 10, stock: 8,    img: 'table-ronde-sauge-dessus-900.webp' },
      { k: 'rect',      cat: 'tables',  n: 'Table rectangulaire 70×180 cm', c: 'table rect.', cp: 'tables rect.',     s: '8 à 10 personnes',             p: 10, stock: 10,   img: 'table-rect-fuchsia-900.webp' },
      { k: 'mange',     cat: 'tables',  n: 'Mange-debout 80×110 cm',        c: 'mange-debout', cp: 'mange-debout',    s: 'pour un cocktail',             p: 7,  stock: null, img: 'mange-debout-habille-900.webp' },
      { k: 'arche',     cat: 'deco',    n: 'Arche dorée',                   c: 'arche', cp: 'arches',                 s: 'circulaire ou rectangulaire',  p: 40, stock: 2,    img: 'arche-fleurie-900.webp' },
      { k: 'vaisselle', cat: 'deco',    n: 'Kit vaisselle',                 c: 'kit vaisselle', cp: 'kits vaisselle', s: 'verre, couverts, 2 assiettes', p: 2,  stock: 75,   img: 'vaisselle-couvert-complet-900.webp' }
    ],
    /* Décoration : prix sur devis, jamais affiché au client. Yanis fixe le
       montant dans l'app (ligne « Décoration » du devis). Les clés doivent
       rester celles acceptées par la fonction demande_client de la base. */
    deco: [
      { k: 'ballons',   n: 'Arche de ballons',          s: 'couleurs au choix, chiffre lumineux', img: 'arche-ballons-or-900.webp' },
      { k: 'fleurs',    n: 'Fleurs et centres de table', s: 'bouquets, compositions',             img: 'buffet-tournesols-900.webp' },
      { k: 'linge',     n: 'Chemins de table et serviettes', s: 'aux couleurs de ton thème',      img: 'couvert-fuchsia-900.webp' },
      { k: 'lanternes', n: 'Lanternes et bougies',      s: 'pour une ambiance chaleureuse',       img: 'lanterne-sauge-1200.webp' },
      { k: 'buffet',    n: 'Déco de buffet',            s: 'fond, présentoirs, verrerie',          img: 'buffet-anniversaire-900.webp' },
      { k: 'theme',     n: 'Déco à thème',              s: 'Aïd, Noël, anniversaire…',             img: 'iftar-couvert-1000.webp' }
    ]
  };
  if (typeof module !== 'undefined' && module.exports) module.exports = CAT;
  else root.EV_CAT = CAT;
})(typeof self !== 'undefined' ? self : this);
