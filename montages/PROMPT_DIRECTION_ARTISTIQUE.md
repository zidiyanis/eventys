Written for: un Claude qui a déjà scanné le compte Instagram eventys.paris et qui doit maintenant écrire la direction artistique d'Eventys.

# Prompt : écris la direction artistique d'Eventys

Tu as déjà analysé le compte Instagram **eventys.paris** d'Eventys. Eventys est une activité solo de location de mobilier événementiel en Île-de-France (chaises Napoléon, tables, arches, vaisselle), menée par Yanis. Je vais utiliser ce que tu écris comme **directeur artistique** : je m'y référerai pour chaque carte de texte, chaque montage et chaque choix visuel.

Ta mission : produire **un seul fichier `.md`**, `direction_artistique_eventys.md`, qui dit précisément comment Eventys doit se montrer à l'écran.

## Ce que tu dois produire

Le fichier doit contenir ces sections, dans cet ordre :

### 1. Identité en trois phrases
Qui est Eventys, à qui on parle (particuliers qui organisent un événement en Île-de-France), et ce qu'on veut que le spectateur ressente. Pas de slogan inventé.

### 2. Palette
Pour chaque couleur : nom, code hexadécimal, rôle (fond, texte, accent, filet). Donne aussi les couleurs qui **ne doivent pas** être utilisées.

Points de départ relevés sur les visuels existants de Yanis, à confirmer ou corriger avec ce que tu vois sur le compte :
- crème des fiches : `#F6F2F0`
- bordeaux du « EVENT » du logo : `#6F2F2F`
- rouge terracotta du « YS » : `#AF4444`
- texte courant : `#2B2220`

Si les publications du compte utilisent des couleurs différentes, dis-le et propose la palette qui devrait l'emporter, en justifiant.

### 3. Typographie
- Police des titres et des prix, avec sa graisse et sa taille relative
- Police des sous-titres
- Interlettrage (espacement des capitales)
- Casse (capitales, minuscules, phrase)

Référence : les titres des affiches de Yanis sont en Bodoni MT. Confirme si cela correspond aux posts du compte.

### 4. Cartes de texte
Décris précisément :
- forme (rectangle, coins arrondis, rayon en px)
- fond et opacité
- position dans le cadre (en pixels sur 1080x1920)
- marges internes
- filet ou décor, s'il y en a
- nombre de mots maximum par carte (6 maximum d'après les règles de Yanis)

### 5. Zone sûre et cadrage (1080x1920)
- Rien au-dessus de **y = 230**
- Rien au-dessous de **y = 1440**
- **230 px libres à droite** (l'interface Instagram et TikTok recouvre les boutons)
- Pour chacune de ces zones, dis ce qui peut y être posé et ce qui ne le peut pas

### 6. Ouverture commune
Yanis veut que **chaque vidéo commence de la même façon** : le box de stockage qui s'ouvre (clip `IMG_1044`, environ 0,8 à 3,4 s), puis une carte « Bienvenue chez EVENTYS ». Décris :
- la durée idéale de l'ouverture
- la transition vers la suite (coupe, fondu, glissement)
- le texte exact de la carte, et sa hiérarchie (petit, grand, sous-titre)

### 7. Séquence type
Décris le rythme d'une vidéo de 15 à 45 secondes :
- combien de cartes de texte maximum, et à quel intervalle
- durée minimale et maximale d'un plan
- où placer la mise en place finale
- comment finir (une seule action, formulée une seule fois)

Règle de Yanis : **une vidéo ne dépasse jamais 1 minute**.

### 8. Ce qui est interdit
Liste les éléments à ne jamais utiliser, par exemple :
- texte déjà incrusté dans un clip source (règle de Yanis : aucun clip avec texte, y compris ceux de la salle bleue ou des anciennes publications TikTok)
- gris neutre comme fond de carte
- polices par défaut
- filtres qui modifient la couleur des plans
- tout élément qui laisse croire à une société, un SIRET ou une mention légale inventée
- tout visage reconnaissable sans accord, et toute plaque d'immatriculation visible (la plaque `DY-182-TK` apparaît dans plusieurs clips du dossier Contenue Vlog_)

### 9. Mouvement et transitions
- Animation d'apparition des cartes (fondu, durée en secondes)
- Transitions entre plans (coupe sèche, fondu, autre)
- Zoom ou recadrage autorisés, et leur amplitude maximale

Pour les plans filmés en 4K à l'iPhone (dossier Contenue Vlog_), précise si un zoom de plus de 1,35 dégrade trop l'image.

### 10. Ce qui marche sur le compte
À partir de ton analyse du compte, liste les codes visuels qui fonctionnent déjà : formats de post qui reviennent, types de plans, couleurs dominantes, accroches. Donne **un exemple concret** pour chaque point (date, légende ou description du post). Ne rien inventer.

### 11. Ce qui ne marche pas
Ce qui incohérence entre les publications (couleurs qui changent, visuels trop chargés, bio incohérente, etc.), avec les exemples.

### 12. Checklist de validation
Une liste de cases à cocher que je pourrai utiliser pour vérifier une vidéo avant de la proposer à Yanis. Par exemple :
- [ ] durée ≤ 60 s
- [ ] aucun clip avec texte incrusté
- [ ] carte de texte dans la zone sûre
- [ ] couleurs conformes à la palette
- [ ] prix validés par Yanis
- [ ] une seule action finale

## Règles pour ton travail

1. **N'invente aucun chiffre, aucune date, aucun avis client, aucune mention légale.** Si une information manque, écris « non visible » ou « à confirmer avec Yanis ».
2. **Distingue ce que tu observes sur le compte de ce que tu recommandes.** Marque clairement les recommandations.
3. **Ne copie aucun contenu** d'autres comptes. Tu peux décrire des tendances.
4. Écris en **français**, tutoie Yanis dans les parties qui lui sont adressées, et reste concis : c'est un document de référence, pas un essai.
5. Si tu proposes de changer la palette ou la typographie par rapport aux affiches existantes, justifie-le en une phrase et signale-le en gras.

## Fichiers de référence
- Charte actuelle (code) : `H:\eventys\montages\da.py`
- Ouverture et cartes déjà produites : `H:\eventys\montages\01_tout_ce_que_je_loue.mp4`, `02_du_box_a_ta_table.mp4`, `03_40_personnes.mp4`
- Affiches et logo de Yanis : `H:\eventys\Video\rush\Affiches - infos_\`
- Inventaire des rushes : `H:\eventys\montages\INVENTAIRE_RUSHES.md`
- Règles de montage : `H:\eventys\montages\PROMPT_AGENT_CONTENU.md`
- Récapitulatif du stock : `H:\eventys\montages\RECAP_POUR_CLAUDE_INSTAGRAM.md`
