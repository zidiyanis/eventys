/* Eventys — toutes les données du site au même endroit.
   Pour changer un prix, une photo ou le numéro WhatsApp : c'est ici, et nulle
   part ailleurs.

   Refonte du 2026-10-22, après l'audit du site :
   - 5 photos et 1 vidéo sur la page entière (il y en avait 11 et 3) ;
   - les prix ne sont plus écrits qu'une seule fois, dans la liste unique ;
   - plus de galerie, plus de section « comment ça se passe ». */

const EVENTYS = {

  /* ------------------------------------------------------------------
     À REMPLIR : le numéro WhatsApp, au format international, sans + ni
     espace. Exemple pour un 06 12 34 56 78 : "33612345678".
     Tant qu'il vaut null, le site le dit et propose de copier le message.
     ------------------------------------------------------------------ */
  whatsapp: "33783825638",   // 07 83 82 56 38

  instagram: "https://www.instagram.com/eventys.paris/",
  tiktok: "https://www.tiktok.com/@eventys.paris",

  /* Les quatre informations qu'un visiteur doit voir en dix secondes. */
  essentiel: [
    { titre: "Toute l'Île-de-France",
      texte: "Livraison selon la zone, ou retrait au box à Soisy-sous-Montmorency (95)." },
    { titre: "À partir de 3 € la chaise",
      texte: "Prix à la pièce, affichés en entier sur cette page." },
    { titre: "Je livre et je monte",
      texte: "Tables montées, nappes posées, chaises placées. Je repasse tout chercher." },
    { titre: "Réponse dans la journée",
      texte: "Un message WhatsApp, un devis en retour. Rien n'est bloqué avant." }
  ],

  /* Le catalogue. C'est la SEULE liste de prix de la page : elle sert à la
     fois de tarif et de formulaire. prix = euros par pièce. */
  materiel: [
    { id: "chaise", nom: "Chaise Napoléon blanche", prix: 3, unite: "la pièce",
      texte: "Assise garnie, lavée avant chaque location. 2 € en hiver.", parPersonne: 1 },
    { id: "ronde", nom: "Table ronde Ø120 cm", prix: 10, unite: "la table",
      texte: "8 à 10 personnes. Pliante, elle passe les portes.", parTable: 9 },
    { id: "rect", nom: "Table rectangulaire 70×180 cm", prix: 10, unite: "la table",
      texte: "8 à 10 personnes. Pour une seule longue tablée." },
    { id: "mange", nom: "Mange-debout 80×110 cm", prix: 7, unite: "la table",
      texte: "Pour un cocktail ou un vin d'honneur." },
    { id: "arche", nom: "Arche dorée", prix: 40, unite: "l'arche",
      texte: "Ronde ou rectangulaire. Le coin photo." },
    { id: "kit", nom: "Kit vaisselle", prix: 2, unite: "par personne",
      texte: "Deux assiettes, un verre, les couverts dorés.", parPersonne: 1 },
    { id: "nappe", nom: "Nappe", prix: 9, unite: "la nappe",
      texte: "Blanche, repassée, posée par mes soins.", parTable: 9 }
  ],

  /* Les lignes de service : pas de montant inventé. */
  services: [
    { nom: "Retrait au box", valeur: "sur place" },
    { nom: "Livraison en Île-de-France", valeur: "selon la zone" },
    { nom: "Montage sur place", valeur: "compris" }
  ],

  /* Les tailles proposées d'un seul geste. */
  tailles: [30, 50, 80, 120],

  /* La bande : quatre emplacements qui changent d'image chacun leur tour.
     Ajouter une photo = ajouter son fichier dans une de ces quatre listes
     (elle doit exister dans assets/img, voir outils/medias.py). */
  bande: [
    [
      { f: "salle-fuchsia-1200.webp", alt: "Salle de réception dressée, tables rondes et chaises Napoléon" },
      { f: "chaise-rang-900.webp", alt: "Rangée de chaises Napoléon blanches au soleil" },
      { f: "tables-fuchsia-900.webp", alt: "Tables rondes dressées en fuchsia devant une arche fleurie" }
    ],
    [
      { f: "couvert-fuchsia-900.webp", alt: "Couvert dressé, serviette fuchsia et couverts dorés" },
      { f: "couvert-sauge-900.webp", alt: "Assiette à filet doré, serviette verte et couverts dorés" },
      { f: "couvert-chocolat-900.webp", alt: "Couvert dressé, chemin de table chocolat" }
    ],
    [
      { f: "table-rect-fuchsia-900.webp", alt: "Longue table rectangulaire dressée pour un mariage" },
      { f: "vaisselle-couverts-900.webp", alt: "Couverts dorés alignés sur une nappe blanche" },
      { f: "buffet-tournesols-900.webp", alt: "Buffet nappé, bouquet de tournesols" }
    ],
    [
      { f: "arche-fleurie-900.webp", alt: "Arche fleurie et canapé blanc, coin photo" },
      { f: "table-ronde-sauge-dessus-900.webp", alt: "Table ronde dressée, vue du dessus" },
      { f: "table-chocolat-900.webp", alt: "Table d'anniversaire dressée, chemin chocolat et ballons" }
    ]
  ]
};
