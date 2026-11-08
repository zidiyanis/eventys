Written for : monteur-eventys (ou un Claude dans une autre discussion, avec accès à `H:\eventys`) qui va construire ce montage avec `build.py` / ffmpeg.

# Script validé : "Eventys est de retour" — présentation + mascotte

Vidéo de relance d'Eventys (activité en pause depuis 4-5 mois). La mascotte **Eventys** (lapin en peluche, voir `montages/_cartes/Planche d'autocollants de lapins EVENTYS.png` et les 12 PNG détourés dans `montages/_cartes/stickers/`) se présente elle-même, puis le catalogue défile : chaises, vaisselle, tables rondes/rectangulaires, livraison Île-de-France.

**Lis d'abord `REGLES_EQUIPE.md` et `PROMPT_DIRECTION_ARTISTIQUE.md` dans ce dossier — ce fichier ne les répète pas, il les complète pour ce montage précis.**

## Ce qui est déjà validé par Yanis
- Le concept mascotte (le lapin s'appelle Eventys, il se présente).
- Les 12 poses détourées, prêtes à l'emploi (`stickers/00_*.png` à `11_*.png`).
- La palette, prélevée sur ses vrais assets (pas inventée) : crème `#F2F1EF`, bordeaux `#6F2F2F`, rouge accent `#AF4444`.
- Pas de mange-debout dans cette vidéo : aucun rush exploitable (confirmé dans `build.py`, commentaire "Pas d'arche ni de mange-debout").

## Statut des deux points en suspens (tranchés par Yanis le 2026-10-14)
1. **Ouverture.** Confirmé : cette vidéo s'écarte de l'ouverture commune, la mascotte remplace la carte "Bienvenue chez EVENTYS". Voir `REGLES_EQUIPE.md` règle 5 modifiée en conséquence.
2. **Son.** Confirmé en général (règle 7 modifiée) : bruitages et musique autorisés. **Mais pas tout de suite** : Yanis veut d'abord finaliser le visuel. Ne pas produire de son sur cette passe — le garder en section "Son" ci-dessous comme prévisionnel. Une voix pour la mascotte (lue ou IA) est une idée à part, **pas encore validée**, à rediscuter séparément une fois le visuel bouclé.

## Pourquoi ce script existe
Yanis trouve le montage actuel "trop simplet" (zoom statique, coupe sèche systématique, carte qui ne fait que fondre en entrée). Ce qui suit ajoute une vraie couche d'effets, réalisable en ffmpeg pur (le monteur n'a que Bash/ffmpeg, pas d'After Effects), sans sortir du cadre technique déjà posé dans `build.py` (HDR→SDR obligatoire, bt709, CRF18, zone sûre).

## Nouveautés à ajouter au pipeline `build.py`

1. **Zoom animé (Ken Burns), pas statique.** `_chaine_cadrage(zoom)` applique aujourd'hui un zoom fixe sur tout le plan. Remplacer par une interpolation `zoom_start → zoom_end` sur la durée du segment (`zoompan`, ou `crop` avec `x`/`y` en expression de `t`). Amplitude max 1.15 sur les rushes 1080p, **max 1.35 sur les 4K `Contenue Vlog_`** (au-delà ça pixelise, déjà noté dans `PROMPT_DIRECTION_ARTISTIQUE.md`).
2. **Transitions variées entre plans.** Le concat final (`-f concat -c copy`) ne fait que des coupes sèches. Passer par un chaînage `xfade` en `filter_complex` pour les plans "calmes" (fondu 0.3-0.4s), garder la coupe sèche uniquement sur la séquence coulisses (chargement/livraison) où elle sert le rythme. Ça implique de ré-encoder au lieu de `-c copy` — assumé, les plans sont courts.
3. **Compteur de prix animé.** Au lieu d'une carte prix statique qui apparaît d'un coup, générer avec `da.py` une mini-suite (0 €, puis le prix final) et l'enchaîner comme les cartes actuelles (overlay + fade), sur ~0,4 s, pour un effet de montée.
4. **Chorégraphie de la mascotte.** Chaque sticker apparaît par glissade + fondu (`overlay` avec `x` en expression de `t` pour le slide, `fade` alpha pour l'entrée/sortie), jamais posé d'un coup. Détail des poses et des moments : voir le beat sheet.
5. **Grade couleur unifié.** Les essais `_da`, `_da2`, `_da3` existent déjà dans `_verif/` mais aucun n'a été tranché. Avant ce montage, choisir UN réglage (`eq=`/`curves=`) et l'appliquer à tous les segments après le `TONEMAP`.
6. **Vignette + grain très léger.** `vignette=PI/6:mode=backward` + `noise=alls=4:allf=t` à faible intensité, pour sortir du rendu "brut téléphone". À tester sur les sources 4K pour vérifier que ça ne dégrade pas.
7. **Vitesse variable.** Déjà supporté (`speed` dans le tuple de coupe). À utiliser aussi en ralenti (`speed < 1.0`, ex. 0.85) sur le plan hero de fin, pas seulement en accéléré sur les coulisses.
8. **Son — sous réserve d'accord explicite (voir point ⚠️ ci-dessus).** Si Yanis valide : whoosh discret sur les coupes sèches, petit "cling" à l'apparition de chaque prix, nappe musicale libre de droits en fond (à choisir avec Yanis, bibliothèque limitée sur compte pro Instagram).

## Beat sheet complet

Durée visée : ~24 s. Tous les clips et timecodes sont repris de `build.py` (déjà validés nets par `nettete.py` dans des montages précédents), sauf mention contraire.

| T | Durée | Clip (dossier, in-out) | Carte texte | Effet zoom | Transition | Mascotte |
|---|---|---|---|---|---|---|
| 0:00.0 | 2.6s | `IMG_1044` (Contenue Vlog_, 0.8-3.4) | **VOICI EVENTYS** ⚠️ déroge règle 5 | 1.00→1.06 | — (ouverture) | `01_salut_main_levee`, slide depuis la droite à 0:00.8 |
| 0:02.6 | 1.6s | `IMG_1742` (Contenue Vlog_, 3.5-5.1) | ON EST DE RETOUR | 1.00→1.05 | whip-pan 0.15s | sortie en fondu |
| 0:05.0 | 2.4s | `IMG_1049` (Contenue Vlog_, 1.0-3.4) | CHAISE NAPOLÉON — 3€ | 1.00→1.08 | fondu 0.3s | `02_pouce_leve`, bas-droit, 0:05.3-0:07.0 ; compteur 0€→3€ |
| 0:07.4 | 2.1s | `IMG_4054` (Mariages, 0.2-2.3) | VAISSELLE — 2€ | 1.00→1.05 | fondu 0.3s | compteur 0€→2€ |
| 0:09.5 | 1.3s | `IMG_4045` (Mariages, 1.6-3.9, coupé court) | TABLE RONDE OU RECT. — 10€ | 1.00→1.05 | fondu 0.3s | compteur 0€→10€ |
| 0:10.8 | 1.2s | `IMG_1013` (Contenue Vlog_, 2.4-3.6, zoom 1.35) | (suite de la même carte) | 1.10→1.20 | coupe sèche | — |
| 0:12.0 | 3.0s | `IMG_0968` (Contenue Vlog_, 2.0-8.0, ×1.5) | CHARGÉ LE MATIN MÊME | 1.00→1.10 | coupe sèche | — |
| 0:15.0 | 1.7s | `IMG_1716` (Contenue Vlog_, 1.5-4.5, ×1.3) | (continuité, pas de nouvelle carte) | 1.00→1.08 | coupe sèche | — |
| 0:16.7 | 3.0s | `IMG_4046` (Mariages, 5.0-8.0), ralenti ×0.85 à tester | — | 1.00→1.08 | fondu croisé 0.4s | `06_bras_leves_content`, bond à 0:17.2 |
| 0:19.7 | 2.8s | `freeze_finale` sur `IMG_4054` ≈3.3s | MESSAGE PRIVÉ POUR UN DEVIS | fixe | fondu 0.4s | `08_au_telephone`, se pose à côté de la carte, reste jusqu'à la fin |

## Specs de sortie (rappel, déjà dans REGLES_EQUIPE.md)
1080×1920, 30 fps, bt709/tv forcés, libx264 preset slow CRF18, ≤ 1 min (ici ~24s), zone sûre (rien au-dessus de y=230, rien en-dessous de y=1440, 230px libres à droite), une seule action finale.

## Avant de lancer le rendu définitif
- [x] Ouverture mascotte confirmée par Yanis (2026-10-14)
- [x] Son autorisé en général par Yanis (2026-10-14) — mais pas implémenté sur cette passe, visuel d'abord
- [ ] Le grade couleur (`_da`/`_da2`/`_da3`) est tranché une fois pour toutes
- [ ] relecteur-eventys passe la checklist habituelle avant présentation à Yanis

## Hors scope pour l'instant
- Voix de la mascotte (enregistrée ou IA) : idée notée, pas lancée. À rediscuter une fois le montage visuel validé.
- Choix définitif des bruitages/musique : la règle l'autorise maintenant, mais ce montage reste muet tant que le visuel n'est pas bouclé.
