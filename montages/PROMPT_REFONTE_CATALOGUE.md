Written for : monteur-eventys, qui va implémenter le moteur d'effets dans `build.py` puis reconstruire les 4 vidéos ci-dessous. Lire `REGLES_EQUIPE.md` (règles 5 et 7 modifiées le 2026-10-14) et `PROMPT_MONTEUR_retour_eventys.md` avant de commencer.

# Refonte du catalogue de montages Eventys (2026-10-14)

Yanis trouve les montages actuels "trop simplets" et veut un style complètement différent sur **toutes** les vidéos faites jusqu'ici, pas seulement la nouvelle avec la mascotte. Décision pour y arriver : **consolider d'abord, puis appliquer le nouveau moteur d'effets** aux survivants plutôt que de retravailler 6 vidéos dont plusieurs se recoupent.

## Décision de consolidation

Des 6 montages existants, deux sont déjà obsolètes par les propres notes de `build.py` :
- **`2026-10-07_reel_annonce-retour`** : remplacé par `2026-10-07_reel_catalogue` ("script v2 validé par Yanis le 2026-10-07... remplace la première version narrative"). **À archiver, ne pas reconstruire.**
- **`01_tout_ce_que_je_loue`** et **`02_du_box_a_ta_table`** : même ouverture, même table finale, même structure "catalogue générique" / "parcours narratif" que des versions plus récentes et plus abouties. **À archiver.**

**On garde et on améliore 3 vidéos existantes, + la nouvelle vidéo mascotte = 4 vidéos finales :**

| Rôle | Vidéo retenue | Remplace |
|---|---|---|
| Catalogue (prix par article) | `2026-10-07_reel_catalogue` | `01_tout_ce_que_je_loue` |
| Coulisses / parcours narratif | `2026-10-08_reel_du-box-a-votre-table` | `02_du_box_a_ta_table`, `2026-10-07_reel_annonce-retour` |
| Pack chiffré ("40 personnes, combien ?") | `03_40_personnes` | — (unique, rien à remplacer) |
| Retour + présentation mascotte | nouvelle vidéo, script dans `PROMPT_MONTEUR_retour_eventys.md` | — (nouveau concept) |

**Ne rien supprimer** : les 3 montages archivés restent dans `montages\` (ce sont des montages, pas des rushes, mais même règle de prudence). Juste ne plus les proposer en publication une fois les 4 nouvelles versions prêtes.

## Deux trous de contenu à combler, et une question pour Yanis

1. **`03_40_personnes` n'a pas de carte finale "message privé".** Elle finit sur "Livré et monté" sans action claire — ça enfreint la règle "une seule action finale". À corriger : ajouter la carte CTA finale (comme les 3 autres).
2. **`2026-10-07_reel_catalogue` n'affiche aucun prix** sur ses cartes ("Verres en location aussi", "Lanternes dispo en déco", etc.). Pour les verres : ton tableau de prix n'a que le "kit vaisselle" à 2€ (verre + couverts + 2 assiettes) — pas de prix verre seul. Je propose de changer la carte en "Kit vaisselle — 2€" plutôt que "Verres en location aussi" sans prix.
3. **Question pour toi, Yanis** : les **lanternes** ne sont dans aucune de tes grilles de prix. Ce sont des éléments de déco que tu inclus avec une formule (Ramadan par ex.), ou un article à part qu'on a oublié de chiffrer ? Je ne mets pas de prix dessus tant que tu n'as pas tranché.

## Moteur d'effets (à construire une fois dans `build.py`, puis réutilisé partout)

Détaillé dans `PROMPT_MONTEUR_retour_eventys.md`, section "Nouveautés à ajouter au pipeline build.py" — ne pas le redupliquer ici, juste l'implémenter une bonne fois :
1. Zoom animé (Ken Burns), remplace le zoom statique.
2. Transitions xfade variées (fondu sur les plans calmes, coupe sèche gardée sur les séquences coulisses/énergiques).
3. Compteur de prix animé (0€ → prix final, ~0,4s).
4. Chorégraphie mascotte (glissade + fondu, jamais posée d'un coup).
5. Grade couleur unifié (trancher enfin entre `_da`/`_da2`/`_da3`).
6. Vignette + grain léger.
7. Vitesse variable (accéléré déjà utilisé, ajouter le ralenti sur les plans hero).
8. Son : **autorisé par la règle modifiée**, mais **pas sur cette passe** — Yanis veut le visuel d'abord. Construire ces 4 vidéos muettes.

## Les 4 vidéos à construire

### 1. Catalogue (reprend `2026-10-07_reel_catalogue`)
Cut-list de départ : voir `VIDEOS["2026-10-07_reel_catalogue"]` dans `build.py`. Corrections à appliquer : ajouter un prix sur chaque carte qui n'en a pas (voir trous de contenu ci-dessus), garder la carte finale CTA existante (`freeze_finale` sur `IMG_4054`, "Devis en message privé"). Appliquer le moteur d'effets. Mascotte : une apparition courte (`02_pouce_leve`) sur une carte prix, `08_au_telephone` sur la carte finale.

### 2. Coulisses (reprend `2026-10-08_reel_du-box-a-votre-table`)
Cut-list de départ : voir `VIDEOS["2026-10-08_reel_du-box-a-votre-table"]`, extension Noël comprise (si on est encore avant décembre au moment de publier, retirer les 3 plans Noël — à vérifier avec Yanis selon la date de publication réelle). Appliquer le moteur d'effets, notamment le ralenti sur le plan final. Mascotte : une apparition en coin pendant la séquence de chargement (`01_salut_main_levee` ou une pose "aide"), `08_au_telephone` sur le CTA final.

### 3. Pack chiffré (reprend `03_40_personnes`)
Cut-list de départ : voir `VIDEOS["03_40_personnes"]`. Corrections : **ajouter une carte CTA finale** (manquante actuellement). Appliquer le moteur d'effets, notamment le compteur de prix animé (120€, 40€, 80€, puis 240€ en plus gros/plus marqué). Mascotte : `02_pouce_leve` sur la carte "Total — 240€", `08_au_telephone` sur le CTA ajouté.

### 4. Retour + présentation mascotte (nouvelle)
Script complet déjà prêt dans `PROMPT_MONTEUR_retour_eventys.md` — pas de cut-list existante à reprendre, tout est détaillé dans ce fichier.

## Specs communes (rappel)
1080×1920, 30 fps, bt709/tv forcés, libx264 preset slow CRF18, ≤ 1 min par vidéo, zone sûre, une seule action finale par vidéo, aucun prix ou chiffre inventé — tout vient de `CLAUDE.md` ou de ce qui est déjà validé dans `build.py`.

## À la fin
- [ ] Les 4 vidéos sont dans `montages\`, lisibles, 9:16, durée correcte
- [ ] `relecteur-eventys` passe chacune à la checklist de `REGLES_EQUIPE.md`
- [ ] Présentation à Yanis avec légende + CTA, pour validation avant publication
