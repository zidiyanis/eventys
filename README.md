# Site Eventys

Site d'une seule page avec un **devis en trois gestes** qui écrit tout seul
le message WhatsApp du client.

Ouvre `index.html` dans ton navigateur, ou mieux :

```
cd H:\eventys\site-internet
python -m http.server 8123
```
puis `http://localhost:8123`.

---

## ⚠️ La seule chose qui manque : ton numéro WhatsApp

Dans `assets/js/donnees.js`, ligne `whatsapp:` :

```js
whatsapp: "336xxxxxxxx",     // format international, sans + ni espace
```

Tant que c'est `null`, le bouton « Envoyer sur WhatsApp » ne va nulle part :
il copie le message et affiche un avertissement. **Aujourd'hui, personne ne
peut te joindre depuis le site.**

Deux autres choses à me dire quand tu veux :
- une idée de prix de livraison par zone (même approximative) — le total
  affiché n'est pour l'instant que le matériel ;
- tes règles de durée, d'acompte et de caution. Je n'ai rien inventé, donc
  rien n'est écrit là-dessus.

---

## La page, après l'audit du 2026-10-22

Elle est passée de 9 sections à 6, de 16,7 écrans à **7 sur téléphone**
(5 sur ordinateur), de 11 photos à **5**, de 3 vidéos à **1**, et de 7,2 Mo
à **1,7 Mo** au premier chargement.

| Section | Ce qu'elle fait |
|---|---|
| Accroche | Vidéo plein écran, titre « TOUT MONTÉ », le prix de départ et un seul bouton |
| L'essentiel | Les 4 choses à savoir, sur fond bordeaux : zone, prix, service, délai de réponse |
| Votre devis en trois gestes | 30 / 50 / 80 / 120 personnes → la sélection se remplit → le total → WhatsApp. À 1,6 écran du haut |
| Le matériel et les prix | **La seule liste de prix de la page.** Elle sert aussi de formulaire : les + et − changent le devis |
| La bande | Quatre photos au même format, bord à bord |
| Bon à savoir + contact | Deux questions, puis le pied bordeaux |

Ce qui a été supprimé : la galerie de 9 images, la section « comment ça se
passe », la pastille flottante (elle masquait les boutons sur téléphone),
les champs occasion / date / ville / message, le doublon de la liste de prix.
La date et la ville se disent maintenant dans la conversation WhatsApp — le
message généré se termine par une ligne « Ma date et ma ville : » à compléter.

---

## Les images

5 photos et 1 vidéo, choisies une par une. Les 26 autres fichiers restent
dans `assets/img` (sombres, flous, arrière-plans encombrés, doublons) : pour
en remettre une, il suffit de l'ajouter à la liste `bande` de `donnees.js`.

### Refaire les médias
Les originaux dans `H:\eventys\Video\rush` ne sont jamais touchés.

```
python H:\eventys\site-internet\outils\medias.py
```

Le script convertit les HEIC, recadre, retouche doucement, exporte en WebP,
**floute les prénoms des mariés** peints sur l'arche (liste `FLOUS`) et
convertit les vidéos HDR en SDR (sans ça l'image paraît cramée).

---

## Les fichiers

```
site-internet\
  index.html              la page
  assets\css\style.css    toute la charte (crème, bordeaux, Bodoni)
  assets\js\donnees.js    PRIX, PHOTOS, NUMÉRO — c'est ici qu'on modifie
  assets\js\app.js        le moteur (sélection, total, message)
  assets\img\             les images web (seules 5 sont utilisées)
  assets\video\           les clips convertis (seul hero-table est utilisé)
  outils\medias.py        refabrique images et vidéos
  outils\MAGIC_MCP.md     comment activer Magic MCP si tu y tiens
```

## Mettre en ligne

```
cd H:\eventys\site-internet
git init && git add . && git commit -m "Site Eventys"
```
Puis crée le dépôt sur GitHub et active Pages sur la branche `main`.

## Détail assumé

Les images se chargent au fil du défilement. Un outil qui photographie la
page entière sans la faire défiler les verra vides ; un vrai visiteur, non.
Pour contrôler la page sans les animations : `index.html?anim=0`.

## Référencement (Google et les IA)

Ce qui est déjà dans la page :

- **titre et description** écrits pour la recherche : le métier et la zone,
  pas le nom de marque en premier (personne ne cherche « Eventys ») ;
- **données structurées** (`application/ld+json`) : fiche `LocalBusiness` avec
  l'adresse de départ, la zone desservie, le numéro, les réseaux et les sept
  tarifs en `Offer` ; un bloc `Service` ; un bloc `FAQPage`. C'est ce que lisent
  Google et les IA pour répondre « où louer des chaises en Île-de-France » ;
- **sept questions-réponses visibles**, identiques au `FAQPage` (rien de caché,
  sinon Google sanctionne) ;
- **le contenu écrit en dur dans `index.html`** : l'essentiel, les services et
  la liste des prix. `app.js` les réécrit depuis `donnees.js` au chargement,
  mais les robots qui n'exécutent pas le JavaScript — plusieurs robots d'IA —
  voient déjà tout. **Si un prix change dans `donnees.js`, change-le aussi dans
  `index.html`** : `outils/referencement.py` refuse de travailler si les deux
  ne disent pas la même chose ;
- un titre lisible par les moteurs sous le grand « TOUT MONTÉ » (`.lu-seul`) ;
- métadonnées de partage (WhatsApp, Instagram) avec une vraie photo.

Ce qui dépend de l'adresse du site, et qui s'écrit d'une commande :

```
python outils/referencement.py https://ladresse-du-site/
```

Ça pose le `canonical`, l'`og:url`, les images de partage en adresse absolue,
puis écrit `robots.txt` (robots d'IA explicitement autorisés), `sitemap.xml`
et `llms.txt` (la fiche de l'activité en texte, pour les IA). La commande est
rejouable : si l'adresse change, on la relance.

### À faire une fois le site en ligne

1. **Google Search Console** : ajouter le site, envoyer `sitemap.xml`.
2. **Google Business Profile** (fiche d'établissement) : c'est ce qui fait
   apparaître l'activité dans la carte et dans « location de chaises près de
   moi ». C'est le levier le plus fort pour du local, devant le site.
3. Mettre l'adresse du site dans la bio Instagram et TikTok (les liens depuis
   ces profils comptent).

## Mise en ligne sur Vercel

Le site est statique : pas de compilation, Vercel sert les fichiers tels quels.

1. vercel.com → **Add New… → Project** → *Import Git Repository* → `zidiyanis/eventys`.
2. Framework Preset : **Other**. Build Command : vide. Output Directory : vide
   (la racine). Install Command : vide. → **Deploy**.
3. Ensuite, chaque `git push` sur `main` redéploie tout seul. Une branche ou une
   pull request donne une adresse d'essai, sans toucher au site en ligne.

`vercel.json` pose les en-têtes : protections de base (nosniff, anti-iframe,
HSTS) et la durée de cache des médias — un jour dans le navigateur, une semaine
en arrière-plan, pour qu'une photo regénérée par `medias.py` sous le même nom
finisse par remplacer l'ancienne au lieu de rester coincée un an.

`404.html` est servi automatiquement par Vercel sur une adresse inconnue.

### Brancher le nom de domaine

1. Vercel → le projet → **Settings → Domains** → ajouter le domaine.
2. Chez le vendeur du domaine, poser les enregistrements que Vercel affiche
   (en général un `A` vers `76.76.21.21` pour le domaine nu et un `CNAME` vers
   `cname.vercel-dns.com` pour `www`). Le certificat HTTPS se fait tout seul.
3. **Relancer le référencement avec la vraie adresse** :
   ```
   python outils/referencement.py https://le-domaine.fr/
   git add -A && git commit -m "Referencement : nouveau domaine" && git push
   ```
4. Couper GitHub Pages (Settings → Pages → Source : None) pour ne pas avoir
   deux fois le même site en ligne.
