# Eventys — contexte pour Claude Code

Tu travailles avec Yanis (parle-lui en français, tutoiement, réponses courtes et concrètes).

## Le business
Eventys est une activité solo de location de mobilier événementiel en Île-de-France, gérée entièrement par Yanis (préparation, chargement, livraison, montage).
- Instagram : **eventys.paris**. TikTok aussi. Pas de Facebook.
- L'activité était en pause depuis ~4-5 mois et est en cours de relance. Aucune publication récente : on veut publier **souvent et régulièrement**.
- Matériel stocké dans un box à Soisy-sous-Montmorency (Val-d'Oise).
- Pas de société ni de SIRET pour l'instant : ne mets aucune mention légale ou commerciale inventée dans les contenus.

### Catalogue (pour les textes à l'écran)
| Article | Prix |
|---|---|
| Chaise Napoléon blanche | 3 €/pièce (2 € en hiver) |
| Table ronde Ø120 cm (8-10 pers.) | 10 € |
| Table rectangulaire 70x180 cm (8-10 pers.) | 10 € |
| Mange-debout 80x110 cm | 7 € |
| Arche circulaire dorée / rectangulaire dorée | 40 € |
| Kit vaisselle (verre + couverts + 2 assiettes) | 2 €/pièce |
| Nappe (location) | 9 € |

Stock : 100 chaises, 10 tables rectangulaires, 8 tables rondes, 2 arches, 75 kits vaisselle. Panier moyen : ~40 chaises + 4 tables. Livraison en Île-de-France, tarif selon la zone ; certains clients viennent chercher au box.
Vérifie les prix avec Yanis avant de les afficher dans une vidéo : ils peuvent changer.

## Objectif de ce dossier
**Le but final est le montage** : produire, à partir des rushes de Yanis, des Reels/TikTok **adaptés à la clientèle d'Eventys** et assez nombreux pour publier souvent. Pour bien monter, tu dois d'abord **connaître le contenu de chaque vidéo et photo** : on construit donc un **catalogue** de ses rushes (étape 1), puis on monte (voir « Montage »).

## Où sont les fichiers
```
H:\eventys\
  CLAUDE.md                  ← ce fichier
  catalogue_rushes.py        ← le script d'extraction d'images clés
  Video\                     ← anciens zips Google Drive (à ignorer, seront supprimés)
  rushes\                    ← vidéos et photos dézippées (ORIGINAUX)
    Mariages, Noël, Ramadan (+ Promo spécial Aïd mars 2026), Achat (photos HEIC), Contenue Vlog
  rushes\_catalogue\         ← créé par le script (index.json, index.md, planches)
  montages\                  ← vidéos finies (à créer au besoin)
  assets\                    ← logo, musiques, polices (à créer au besoin)
```

## Règles de travail
1. **Ne modifie, ne déplace et ne supprime jamais un fichier de `rushes\`.** Tu écris seulement dans `rushes\_catalogue\`, `montages\` et `assets\`.
2. **Économise les tokens** : traite par lots de 10 fichiers, écris chaque fiche dans un fichier dès qu'elle est faite, ne regarde jamais deux fois la même planche, et dis où tu en es à chaque lot. Demande avant de lancer une opération longue ou coûteuse.
3. Le script reprend où il s'est arrêté : si ça plante, relance la même commande.
4. **N'invente rien.** Si une planche ne suffit pas à juger (vidéo longue, image floue), écris « aperçu partiel » et dis ce qui manque.
5. Les photos HEIC (dossier Achat) peuvent échouer : convertis-les en JPG dans `_catalogue\converted\` avec ffmpeg, sans toucher aux originaux.
6. Le dossier **Contenue Vlog** vient d'un autre compte Google (pas de Yanis). Catalogue-le, mais marque ses clips « à valider avec la personne avant publication ».

## Lancer le catalogue
Dans le terminal, depuis `H:\eventys` :
```
python catalogue_rushes.py "H:\eventys\rushes"
```
Si tu veux réduire le coût : dans le script, passe `MAX_FRAMES` à 6, `FRAME_WIDTH` à 320 et `COLS` à 3.

Ensuite, pour chaque entrée de `_catalogue\index.json` qui a une `sheet` :
1. Ouvre l'image `planche.jpg` correspondante et regarde-la.
2. Écris `_catalogue\fiches\<nom>.md` avec :
   - Fichier, dossier, date, durée, format (vertical/horizontal)
   - Contenu scène par scène, avec horodatages approximatifs (déduits de `frame_times_s`)
   - Mobilier et déco visibles (types et quantités approximatives)
   - Qualité : lumière, stabilité, cadrage, netteté
   - Points forts / défauts
   - Usages possibles pour un Reel/TikTok (accroche, timelapse, avant/après, coulisses, pack mariage…)
   - Recadrage 9:16 possible ? (oui/non et pourquoi)
   - Confidentialité : visages reconnaissables, enfants, plaques, adresses
   - Note de réutilisation sur 5
3. À la fin, écris `rushes\CATALOGUE_EVENTYS.md` avec : un résumé par sous-dossier, le top 10 des meilleurs clips à réutiliser, les plans qui manquent pour de bonnes vidéos, et les clips à flouter ou éviter.

## Après le catalogue
`CATALOGUE_EVENTYS.md` devient la mémoire du dossier : **lis-le en premier à chaque session**, au lieu de reregarder les images. Les montages se font ensuite avec ffmpeg dans `montages\`, à partir des clips choisis dans le catalogue.

## Montage (le vrai but)
**Clientèle** : des particuliers d'Île-de-France qui organisent un événement et veulent voir vite ce qu'ils peuvent louer, combien ça coûte et que c'est simple. Les dossiers de rushes (Mariages, Noël, Ramadan/Aïd) suggèrent ces occasions : confirme-les avec Yanis plutôt que de les supposer.

**Format** : 9:16, 15 à 45 s, accroche dans les 2 premières secondes, texte à l'écran de 6 mots maximum par carte et dans la zone sûre (rien au-dessus de y=230 ni au-dessous de y=1440 sur 1080x1920, et 230 px libres à droite), prix visibles, **une seule action finale** (à valider avec Yanis, par exemple « écris-nous en message privé pour un devis »).

**Formats à proposer** : timelapse d'installation, avant/après d'une salle, « X chaises + Y tables pour N personnes » avec le prix total, coulisses (chargement, livraison), packs tout prêts selon l'occasion, plan final d'ambiance.

**Méthode** :
1. Pour chaque montage, propose d'abord 2 ou 3 idées en citant les clips du catalogue. Attends le choix de Yanis.
2. Monte avec ffmpeg dans `montages\`, sans toucher aux originaux.
3. Vérifie le résultat (durée, format 9:16, quelques images extraites) avant de dire que c'est fini.
4. **Propose des améliorations sans attendre qu'il les demande** : voix off, sous-titres incrustés, musique, cartes de prix, ralenti ou accéléré, avant/après, carte de fin.

**Voix** : le plus authentique est que Yanis enregistre lui-même sa voix (son téléphone suffit) ; tu la synchronises avec le montage et tu ajoutes les sous-titres. Une voix de synthèse est possible, mais présente ses limites avant de la proposer.

**Outils et espace disque** : avant d'installer un programme ou un modèle (sous-titrage automatique de type Whisper, synthèse vocale…), demande à Yanis. Il lui reste environ 6 Go libres sur C: : installe ce qui est lourd sur H:.

**Musique** : uniquement libre de droits, ou laisse Yanis l'ajouter dans l'application au moment de publier (la bibliothèque musicale peut être limitée sur un compte pro).

**Tu ne publies jamais.** Tu prépares la vidéo, la légende et le texte ; c'est Yanis qui publie.

## Skills Instagram (pack `ig-*`)
Installés dans `.claude/skills/` de ce dossier : `ig-reel`, `ig-caption`, `ig-plan`, `ig-human`. Ils **écrivent** (accroches, script, texte à l'écran, plan de beats chronométré, légendes, planning de la semaine). Ils **ne montent pas** la vidéo et ne publient pas.

Enchaînement : catalogue → choix des clips → `/ig-reel` (accroche, texte à l'écran, beat sheet) → montage ffmpeg qui suit le beat sheet → `/ig-caption` → Yanis publie. `/ig-plan` sert à organiser la semaine.

- Ces skills sont écrits pour l'anglais et pour des créateurs qui parlent face caméra. Écris tout en **français** et adapte-les à des vidéos de mobilier.
- Les scores d'accroche (`hookscore.py`) utilisent des listes de mots anglais : sers-t'en pour comparer deux options, pas comme un verdict.
- Les skills lisent `~/.claude/instagram/voice.md` (profil de voix de Yanis). S'il n'existe pas, demande à Yanis de répondre à quelques questions ou de te donner 3 de ses anciens posts. **Ne l'invente pas.**
- Ne fabrique jamais un chiffre, un avis client ou une preuve : utilise seulement ce que contient ce fichier ou ce que Yanis te donne.
