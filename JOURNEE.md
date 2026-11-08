# La journée Eventys — ce qui tourne, et ce qu'il reste à faire à la main

## En une phrase

Une vidéo par jour, publiée seule sur Instagram et Facebook, plus des
stories. TikTok reste manuel : deux minutes dans un dossier déjà prêt.

---

## Les règles de production, à ne jamais enfreindre

Elles viennent de tes retours successifs. Le relecteur les vérifie avant
chaque publication.

### Le script
- **Le lapin parle du début à la fin.** Pas de plan muet où une étiquette
  s'affiche seule : s'il montre un produit, il en parle.
- **Écrire avec les accents.** « employé », « Napoléon », « Île-de-France »,
  « ça ». Sans eux, ElevenLabs prononce autre chose — c'est arrivé.
- **Boucle de fin obligatoire.** Dernier plan = même rush et même cadrage
  que le premier, joué à l'envers pour que la dernière image soit la
  première. Réplique : « Allez. On recommence. »
- **Demander l'abonnement**, comme dans la vidéo du 20 octobre :
  « Et abonnez-vous. C'est gratuit, et ça nous aide. »
- **Un prix dans les 2 premières secondes.** C'est le levier le mieux
  documenté de l'étude concurrentielle : ×15 à ×20 de vues.
- **Jamais de chiffre de stock.** Annoncer « 100 chaises » fixe un plafond
  et disqualifie un client qui en veut plus.
- **Jamais « livraison comprise ».** Elle est facturée selon la zone.

### Le montage
- **Un plan = une réplique.** La durée du plan est taillée sur la durée de
  l'audio, jamais l'inverse.
- **Varier les rushes.** Seule exception : l'ouverture du box, qui reste
  la signature. Tout le reste doit tourner d'une vidéo à l'autre.
- **Aucune vitesse différente de 1,00** sans interpolation : ça saccade.
- **Zone sûre** : rien au-delà de x=850, rien sous y=1440, rien au-dessus
  de y=230.
- **Trois bandes qui ne se croisent jamais** : mascotte, étiquette de prix,
  sous-titre.
- **La mascotte ne flotte pas** : elle pose ses pieds sur une ligne de sol.

### Le son
- Voix **Jonathan** (`vCsptCe91UKbZe2sIB2T`), jamais une autre.
- Lit sonore sous la voix, qui s'efface quand elle parle.
- **−14 LUFS**, c'est la norme des plateformes.

### Le format
- H.264 **High**, **yuv420p**, AAC 48 kHz, étiquettes bt709.
  Le yuv444p est refusé par Instagram et TikTok.
- **Stories vidéo** : débit plancher 5 Mb/s. Une image fixe compressée en
  `crf` ne pèse qu'1 Mb/s et Instagram la refuse (erreur 2207077).

### La vignette du Reel — ne jamais l'oublier
Instagram prend la **première image** comme couverture. Notre vidéo ouvre
sur le rideau du box : une vignette grise au milieu d'une grille de tables
dressées, ça détonne et ça abîme le profil.

**Toujours passer un `thumb_offset`** qui pointe sur une table dressée.
Troisième argument de `publier.py` :

```
python meta/publier.py <video> <legende.txt> 27.0
```

Plus largement : **chaque publication doit comporter de la décoration
finalisée**, pas seulement des coulisses. La grille du profil se regarde
avant les vidéos.

### La chaîne de validation — trois étapes, aucune facultative

**1. Le directeur artistique** décide du thème, le matin.
Il connaît la rotation, ce qui a déjà été publié, les rushes disponibles et
les enseignements de l'étude concurrentielle. Il propose UNE chose, pas
trois, et signale ce qui cloche au lieu de le taire.

**2. Je produis.** Script, voix, montage, stories.

**3. Le relecteur contrôle la vidéo finie — AVANT publication.**
C'est l'étape qui a été sautée le 22 octobre, et c'est elle qui aurait vu
que le lapin ne parlait pas et que l'image tremblait. Il regarde les images
une par une, lance le contrôle automatique, et vérifie les règles de ce
fichier. **Rien ne part sans son passage.**

Le contrôle automatique ne le remplace pas : il mesure, il ne juge pas le
sens des images. Un cadrage qui ne montre pas le produit, une phrase qui
ment, une marque tierce lisible — aucune machine ne les voit.

### Rien ne se supprime — donc rien ne se publie sans contrôle

**L'API Instagram ne sait pas supprimer une publication.** Aucune permission
n'existe pour ça. Une erreur publiée reste en ligne jusqu'à ce que Yanis
l'efface à la main — ça lui est arrivé cinq fois les 21 et 22 octobre.

La règle n'est donc pas « supprimer l'ancien », qui est impossible, mais
**ne jamais publier ce qui n'a pas été vérifié**.

`meta/controle.py` le fait automatiquement, et `publier.py` refuse de
publier un fichier qui échoue :

| Contrôle | Seuil | Pourquoi |
|---|---|---|
| Tremblement (montage de **photos**) | 0,20 max | tout mouvement vient de `zoompan` : au-delà, il faut supprimer le zoom |
| Tremblement (montage de **rushes**) | 5 × la médiane du montage, plafonné à 6,0 | un seuil absolu rejetait le Reel du 20/10, pourtant le meilleur contenu (pire plan 4,34). La question est « ce plan bouge-t-il plus que les autres », pas « bouge-t-il » |
| Netteté par plan | moyenne pas sous 45 % de la médiane, **creux pas sous 25 %** | ajoutée le 26/10 : un panoramique trop rapide donne une image **traînée**, que la mesure de tremblement trouve calme. Deux plans sur dix étaient passés |
| Format d'image | yuv420p | le yuv444p est refusé par les plateformes |
| Fréquence du son | 48 000 Hz | à 96 kHz, beaucoup de lecteurs restent muets |
| Niveau sonore | −16 à −12 LUFS | norme des plateformes |
| Durée | 3 à 90 s | limite des Reels |

`--forcer` passe outre, mais ça doit rester exceptionnel et assumé.

### Jamais deux fois le même contenu — la règle la plus chère de toutes

Le Reel `CALCUL_50.mp4` est parti **trois jours de suite**, les 26, 27 et
28 octobre. Cause : `_a_publier_aujourdhui\` n'était jamais vidé après une
publication, et `publier_17h.py` publie ce qu'il y trouve.

Le prix, mesuré :

| | Vues | J'aime | Enregistrements |
|---|---|---|---|
| 26/10, première diffusion | 17 162 | 194 | 228 |
| 27/10, **même vidéo** | 2 631 | 27 | 24 |

Six fois moins. L'algorithme reconnaît un contenu déjà diffusé et cesse de
le montrer ; l'abonné qui l'a vu passe. Et rien ne se supprime chez
Instagram.

**Deux protections indépendantes, parce qu'une seule a déjà échoué :**

1. `publier_17h.py` **déplace** ce qu'il a publié dans
   `journal\deja_publie\<date>\`. Le dossier du jour est vide le lendemain
   matin ; s'il ne l'est pas, la production du matin n'a pas tourné.
2. `meta/doublon.py` **refuse** de publier un contenu déjà vu, sur trois
   mesures :

| Mesure | Répond à | Verdict |
|---|---|---|
| sha256 du fichier | est-ce exactement ce fichier ? | refus |
| Accroche de la légende | l'abonné lira-t-il la même phrase ? | refus |
| Empreinte de 16 images (dHash) | est-ce la même vidéo, même réexportée ? | refus au-delà de 55 % |
| Images communes avec une publication passée | repuise-t-on dans les mêmes rushes ? | alerte au-delà de 35 % |

Les seuils viennent de mesures, pas d'intuitions : une vidéo comparée à sa
propre copie Instagram tombe à 75 % (le réencodage de Meta abîme
l'empreinte), un vrai inédit plafonne à 25 % à cause du plan d'ouverture sur
le box, commun à toutes nos vidéos. On coupe au milieu.

Le registre est `meta/publie.json`. Il se reconstruit depuis **ce qui est en
ligne**, pas depuis nos fichiers :

    python meta/doublon.py --rattraper          # relit l'API, retélécharge
    python meta/doublon.py <video> [legende]    # teste avant de publier
    python meta/doublon.py                      # liste l'historique

Les stories suivent la même règle, en plus souple : une story déjà publiée
depuis moins de **14 jours** est écartée de la série du jour sans faire
échouer les autres. Au-delà, plus personne ne s'en souvient.

### Le cadrage — la règle qui a coûté le plus cher
Les photos sont des verticales 9:16 prises au téléphone. **Un recadrage
automatique au centre est interdit** : il tombe sur la nappe vide et coupe
les couverts, le verre, la chaise.

Trois règles, dans cet ordre :

1. **Le produit doit être le sujet.** Si la vignette annonce « kit
   vaisselle », on doit voir l'assiette, les couverts et le verre. Recadrer
   SUR le produit est non seulement permis, c'est exigé — « bien cadrer »
   ne veut pas dire « ne jamais recadrer ».
2. **Ne jamais couper un objet qui touche deux bords opposés.** Les
   couverts et le verre occupent toute la hauteur : pour eux, photo
   entière obligatoire (`entiere=True`).
3. **Regarder chaque image au format réel avant de publier.** Une planche
   de vignettes ne montre pas le défaut — c'est comme ça que trois
   carrousels ratés sont partis le 21 octobre.

### Le travelling des stories
`zoompan` avance par pixels entiers : sur un mouvement lent, ça tremble.
On calcule donc au double de la définition puis on réduit. Vérifier avec la
mesure d'irrégularité : en dessous de 0,25, c'est fluide.

---

## La variété, pour ne pas lasser

Ne jamais publier deux jours de suite le même type. Rotation :

| Jour | Format |
|---|---|
| 1 | Vidéo lapin — catalogue et prix |
| 2 | Carrousel **sans le lapin** — décoration finalisée |
| 3 | Vidéo lapin — coulisses (nettoyage, chargement) |
| 4 | Story seule, parfois **une seule photo** |
| 5 | Vidéo lapin — une occasion (mariage, anniversaire, Aïd) |
| 6 | Carrousel — mise en place, plans de chaises |
| 7 | Avant/après, **quand les prises existeront** |

Les stories alternent **beige et bordeaux**. Deux beiges de suite se
confondent.

### Saison — arbitrage du 27/10

**Noël ne se publie pas avant mi-novembre** (décision de Yanis). Le Reel
« Votre repas de Noël » est monté et contrôlé, il attend la date :
`montages/videos13.py` → `montages/NOEL_12_son.mp4`.

**La chaise reste à 3 € en décembre** : le tarif hiver à 2 € ne couvre pas
les fêtes.

**Les deux appels à la fin**, comme le Reel du 20/10 : « Écrivez-moi » puis
« Abonnez-vous ». Cela tranche la contradiction entre ce fichier et
`REGLES_EQUIPE.md` (« une seule action finale »), qui ne s'applique donc
qu'à l'appel commercial.

### Choisir une fenêtre de coupe

**Jamais sur la vignette source en paysage.** Le 9:16 n'en garde qu'une
bande et un recadrage centré garde le haut du mur en coupant la table.
Trois montages ont été jetés pour ça, dont un plan « 12 kits vaisselle »
qui filmait un sapin.

    python montages/reperage9x16.py <stem> <dossier> [pas_en_s]

rend la planche du rush **dans le cadre final**, à trois hauteurs. Le
paramètre `ancre` (0 = haut, 1 = bas) se passe ensuite à `styles2.plan` et
à `story_clip.clip`.

### Les rushes tournés à la verticale — le piège du recadrage

Beaucoup de rushes portent une métadonnée `rotation=-90` : **tout le
dossier `Contenue Vlog_`**, par exemple. `ffprobe` annonce 3840x2160, mais
ffmpeg les redresse au décodage et travaille sur du **2160x3840, du 9:16
exact**. Sur ceux-là, rien n'est jamais recadré, et ni `ancre` ni `ancre_x`
n'ont le moindre effet : ce qu'on voit dans le rush est exactement ce qu'on
aura à l'écran.

    ffprobe -v error -select_streams v:0             -show_entries stream_side_data=rotation <fichier>

Ça change la méthode : pour un rush vertical, inutile de passer par
`reperage9x16.py`, la vignette source suffit. Pour un rush réellement en
paysage (Noël, `Mise en place_`) ou en 4:3, le repérage reste obligatoire.

**`ancre_x`** (0 = bord gauche, 1 = bord droit) a été ajouté le 28/10 à
`styles.plan`, `styles2.plan` et `story_clip.clip`. Il sert surtout à
sortir du cadre ce qui ne nous appartient pas : un véhicule floqué, une
plaque, un sac de marque. C'est la raison la plus fréquente de jeter un
plan par ailleurs bon.

### Ne jamais vendre ce qu'on ne montre pas — et l'inverse

Deux erreurs symétriques, toutes deux rattrapées de justesse :

- **Annoncer un produit absent de l'image.** Une carte « 12 kits vaisselle »
  posée sur un sapin, une carte « arche dorée » posée sur des lettres
  lumineuses qui ne sont pas à nous. Trois montages jetés pour ça.
- **Montrer ce que le script exclut.** Le 28/10, le Reel « juste des
  chaises, sans rien d'autre à louer » se terminait sur deux plans où on
  porte des **tables pliantes** — au moment exact du message final.
  Relevé par le relecteur, pas par moi, et aucune mesure ne pouvait le voir.

La question à se poser sur chaque plan n'est donc pas seulement « est-ce
que le produit annoncé est là », mais « est-ce que quelque chose dans
l'image contredit ce que la voix promet ».

### Deux zones sûres différentes, et il faut le savoir

| Support | Dernière encre | Pourquoi |
|---|---|---|
| **Reel** | y = 1440 | la légende, le nom de compte et les boutons occupent tout le bas |
| **Story** | y = 1670 | il n'y a que la barre « Envoyer un message » |

Le cartouche de `story_clip.py` descend jusqu'à ~1630 : **c'est voulu**, et
c'est plus lisible que de tout tasser au milieu. Les cartes fabriquées de
`stories2.py` s'arrêtent plus haut, à 1440, parce qu'elles portent des prix
qu'on doit pouvoir lire sur une capture d'écran.

### La zone sûre des stories fabriquées

Les cartes de `stories2.py` empilaient leurs éléments **depuis le haut** :
avec une photo de 820 px, le dernier texte finissait vers y=1750, derrière
la barre de réponse d'Instagram — invisible pour tout le monde, et jamais
vu parce qu'on ne regardait que la vignette.

Elles sont désormais **ancrées par le bas** : on part de y=1420 et on
remonte, et c'est la photo qui absorbe ce qui reste. Vérification :

    dernière ligne d'encre de la carte ≤ 1440

**Débit** : `-b:v 5M` donnait 4,15 Mb/s réels — libx264 n'atteint pas sa
cible sur une image presque immobile. Il faut viser au-dessus et imposer un
`minrate` **supérieur** au plancher, pas égal : `-b:v 7M -minrate 5500k`.

### Les stories ne sont pas optionnelles

Oubliées le 22 puis le 26 octobre. Yanis a dû le redire deux fois : *« à
chaque fois il faut que tu utilises d'autres vidéos, d'autre contenu des
rushes, et il faut que ce soit plus varié »*. **Un jour sans stories est un
jour raté, même si le Reel est bon.**

Composition obligatoire, appliquée par `montages/serie_jour.py` :

| Règle | Pourquoi |
|---|---|
| **Au moins 3 clips de rush** habillés (`story_clip.py`) | une série faite de cartes fabriquées ressemble à un catalogue |
| **Au plus 2 cartes fabriquées** (`stories2.py`) | elles servent de respiration, pas de contenu |
| **Aucun rush déjà vu dans le Reel du jour** | sinon la story ne donne aucune raison d'être regardée |
| **Jamais de capture d'écran** | demandé explicitement : « pas juste des screen » |
| Logo **crème uni sur voile sombre**, en haut au centre | le logo bicolore disparaît sur une chaise blanche comme dans un box sombre |
| Si un rush n'a que 2 s exploitables → `va_et_vient=True` | repasser sur 2 bonnes secondes vaut mieux qu'en montrer 4 dont 2 vides |

Le partage du Reel en story reste **à la main** : l'API ne sait pas créer
la vignette cliquable qui renvoie vers la publication.

---

## Ce qui est automatique

1. Génération du script et de la voix
2. Montage, calé sur la durée des répliques
3. Contrôle par le relecteur, sur les règles ci-dessus
4. Publication du Reel sur **Instagram** et **Facebook**
5. Publication des **stories** (vidéos sonorisées)
6. Préparation du dossier TikTok

## Ce qui reste à ta main

- **TikTok** : `A_PUBLIER/<date>/`, tout y est. Deux minutes.
- **Les « à la une »** : l'API ne sait pas épingler. Si une story mérite
  d'y rester, ajoute-la depuis ton téléphone dans les 24 h.
- **Le partage du Reel dans ta story** avec la vignette cliquable :
  seule l'application sait le faire.

---

## Ce qui débloquerait le reste

**Un site.** Il lèverait d'un coup : la vérification de domaine TikTok,
les conditions d'utilisation, la politique de confidentialité. C'est le
seul obstacle restant à l'automatisation complète.

**Les prises qui manquent**, listées dans `PRISES_A_TOURNER.md` :
le vrai avant/après et le plan large du stock.


## Une planche de triage sert à écarter, jamais à valider

*Ajouté le 2026-10-29.*

`montages/triage.py` prend **une** image par rush, à 45 % de sa durée. C'est
parfait pour répondre à « lequel de ces vingt clips montre mon sujet ». Ça ne
répond pas à « ce plan est-il propre », parce qu'un plan de trois secondes
contient quatre-vingt-dix images et qu'on en a regardé une.

Le 29/10, j'ai écrit dans `videos16.py` que les fenêtres avaient été choisies
pour exclure le bougeoir à croissant de lune. C'était vrai sur l'image que
j'avais regardée et faux sur le plan : sur le plan des kits vaisselle, le
croissant entrait en plein cadre pendant les 1,5 dernières secondes. Le
relecteur l'a vu, pas moi.

**La règle :** un élément qu'on veut tenir hors du cadre se vérifie sur toute
la fenêtre, pas sur une image — un balayage à 0,6 s d'intervalle sur le
montage final, avant de dire que c'est propre. Et quand on écrit dans un
commentaire « vérifié », on dit *comment* : sinon la note suivante hérite
d'une certitude qui n'a jamais été mesurée.

Même famille que « ne jamais vendre ce qu'on ne montre pas » : ce sont deux
écarts entre ce qu'on affirme et ce que contient l'image.

---

## Bruitages (valides par Yanis le 2026-11-04)

Banque : `assets/son/sfx/` (16 sons generes avec ElevenLabs). Module :
`montages/sfx.py`.

- `sfx.ajoute(video, evenements, sortie)` place des sons sur une video deja
  sonorisee, sans reencoder l'image. Chaque son est regle par son PIC
  (mesure automatique) : les sons ElevenLabs sortent a des niveaux tres
  differents (`ding_total` quasi muet, `oups` tres fort).
- `sfx.evenements_standard(...)` : pop a chaque etiquette de prix, whoosh a
  chaque coupe, ding sur le total, pop double sur l'appel final, **aucun son
  sur la boucle de fin**. Premier usage : `montages/videos19.py`
  (sortie `*_sfx.mp4`).
- Ne pas depasser environ un son par seconde, et ne jamais en mettre sur le
  tout dernier instant (la video boucle).
- Apres ajout, relancer `meta/controle.py` : le niveau doit rester entre
  -16 et -12 LUFS.
