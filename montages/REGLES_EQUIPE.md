Written for : les agents de l'équipe Eventys (directeur artistique, monteur, relecteur) et Claude qui les coordonne.

# Règles communes de l'équipe Eventys

Ce fichier est la référence partagée. Les trois agents le lisent avant de travailler. En cas de conflit entre une règle d'agent et ce fichier, **ce fichier gagne**.

## Chemins
- Rushes originaux (lecture seule) : `H:\eventys\Video\rush\`
- Catalogue : `H:\eventys\Video\rush\_catalogue\CATALOGUE_EVENTYS.md` et `index.json`
- Suivi de rotation : `H:\eventys\Video\rush\_suivi\SUIVI_ROTATION_CONTENU.md`
- Montages : `H:\eventys\montages\` (les 3 vidéos de référence y sont : `01_tout_ce_que_je_loue.mp4`, `02_du_box_a_ta_table.mp4`, `03_40_personnes.mp4`)
- Vidéos prêtes à publier : `H:\eventys\montages\pret_a_publier\`
- Outils : `H:\eventys\tools\bin\` (ffmpeg et ffprobe)
- Scripts de montage : `H:\eventys\montages\build.py`, `da.py` (cartes de texte), `nettete.py` (netteté)

**Vocabulaire** : un **rush** est un fichier original de `Video\rush\`. Un **montage** est une vidéo produite à partir de rushes. Les trois vidéos de référence sont des montages, pas des rushes.

## Règles de Yanis (non négociables)
1. **Durée : jamais plus d'1 minute.** Viser 15 à 45 s.
2. ~~Aucun rush qui porte déjà du texte incrusté.~~ **Levée le 2026-10-15.** Les clips de `Contenu tiktok _`, `Affiches - infos_`, `Mariages\12941d2e...mov` et la promo Aïd sont de nouveau utilisables. À recadrer pour sortir le texte du champ quand c'est possible ; ne jamais laisser apparaître le filigrane « Ys.événement » (autre nom de marque).
3. **Une seule action finale**, validée par Yanis, formulée une seule fois.
4. **Finir par une mise en place finale** (tables dressées), pas seulement les produits un par un.
5. **Ouverture commune, sauf concept différent assumé.** Par défaut : le box qui s'ouvre (`Contenue Vlog_\IMG_1044.MOV`, environ 0,8 à 3,4 s), puis la carte « Bienvenue chez EVENTYS ». **Modifié le 2026-10-14** : une vidéo au concept clairement différent (ex. la mascotte Eventys se présente) peut s'en écarter — le poser explicitement dans le script, pas le faire en silence.
6. ~~Yanis publie toujours.~~ **Levée le 2026-10-15** : Claude est autorisé à publier. **Mais ce n'est pas encore possible techniquement** — il faut un accès API (compte Instagram Business relié à une page Facebook, app développeur TikTok validée) et les identifiants. Tant que ce n'est pas en place, Yanis publie dans les faits.
7. **Son.** **Modifié le 2026-10-14** : les bruitages et la musique sont autorisés en général (plus besoin d'un accord séparé à chaque montage). **Restent à l'étude, pas encore autorisés en production** : une voix pour la mascotte et tout audio généré par IA — décision à prendre plus tard, pas tant qu'on n'a pas tranché le visuel.
8. **N'invente rien** : prix, chiffre, mention légale, SIRET (il n'y en a pas).
9. **Avis clients : uniquement de vrais propos.** Yanis a demandé le 2026-10-15 de pouvoir écrire des avis parce que des clients le remercient au téléphone sans jamais le mettre par écrit. On reste sur du vrai : Yanis rapporte ce que le client a réellement dit, Claude le met en forme. **Aucun avis inventé, aucun prénom ou profil de client fabriqué** — un faux avis est une pratique commerciale trompeuse (Code de la consommation, art. L121-2 et suivants), sanctionnée en France, et c'est aussi une cause de suppression de compte sur les plateformes. Discussion en cours, voir le compte rendu dans la conversation.

## Qualité technique
- Format 9:16, **1080x1920**, 30 images/s.
- ~~Aucun rush de moins de 1080 px.~~ **Levée le 2026-10-15.** Les 720p et moins (`IMG_1534`, `b82025e7`, `4da75381`, `IMG_1536`, `IMG_1537`, les `UUID.mp4` de `Mariages`, `Mise en place_` en 720p) sont utilisables. **Deux garde-fous** : en plans courts seulement, et jamais juste à côté d'un plan 4K dans la même vidéo — l'écart de définition se voit immédiatement et fait amateur.
- **Rushes iPhone en HDR** (bt2020, HLG) : convertir en SDR avec la chaîne `TONEMAP` de `build.py`, puis forcer les étiquettes `bt709`. Sans cela, l'image est cramée.
- **Zone sûre** : rien au-dessus de **y = 230**, rien au-dessous de **y = 1440**, **230 px libres à droite**.
- Couper sur les passages nets, mesurés avec `nettete.py`.

## Accords et plaques
- **`Contenue Vlog_` (91 vidéos)** : **accord de la personne filmée obtenu** (confirmé par Yanis le 2026-10-07). Ces clips sont utilisables.
- La plaque **DY-182-TK** est celle du **camion d'Eventys** : pas de flou nécessaire.
- Les montages `01`, `02` et `03` sont donc publiables, sous réserve des autres règles (durée, texte, validation de Yanis).
- Si un nouveau clip montre une personne qui n'a pas donné son accord, le signaler à Yanis avant usage.

## Saison
**Règle fixe levée le 2026-10-15, remplacée par du jugement.** Plus d'interdiction de date : on se cale sur la fête réelle et sur le jour de publication.
- Un marqueur de saison (croissant de lune, sapin, ballons d'anniversaire) se publie **quand la fête approche**, pas au hasard : Noël à partir de mi-novembre, Ramadan/Aïd dans le mois qui précède, etc.
- Hors de cette fenêtre, préférer les plans neutres — un sapin en juin ne fait pas « intemporel », il fait « vieux stock ».
- Clips concernés : `Ramadan_` croissant de lune (`IMG_9452, 9454, 9441, 9449, 9398, 9400`), tout le dossier `Noël`, `Anniversaire_`.

## Organisation de l'équipe
Le chef d'équipe est **Claude principal**, qui parle avec Yanis. Les agents ne se parlent pas entre eux.

1. Yanis demande du contenu → **directeur-artistique-eventys** propose **une** idée.
2. Yanis répond **VALIDER** ou **REFUSER**.
3. Si VALIDER → **monteur-eventys** assemble le montage à partir du script validé.
4. Ensuite **relecteur-eventys** contrôle le fichier avec la checklist. Si un point échoue, le monteur corrige.
5. Claude principal présente le résultat à Yanis, avec la légende et le CTA validés. **Yanis publie.**
6. Le suivi `SUIVI_ROTATION_CONTENU.md` est mis à jour à chaque étape.

## Ce que les agents ne font jamais
- Publier.
- Choisir un rush qui n'est pas dans le script validé.
- Ajouter un prix ou une mention non confirmée par Yanis.
- Modifier ces règles.
