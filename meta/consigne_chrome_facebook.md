# Consigne extension Chrome — ajouter la publication sur la Page Facebook

Colle le bloc entre les tirets dans l'extension Claude, Facebook connecté.

---

Tu travailles dans mon navigateur sur mon compte Facebook. L'application est
déjà configurée et fonctionne pour Instagram. Il manque UNE autorisation pour
pouvoir publier aussi sur la Page Facebook elle-même.

CONTEXTE DÉJÀ EN PLACE — ne refais pas ces étapes
- Application Meta « Eventys Publication », identifiant 1837815554329232
- Page Facebook « Eventys.paris », identifiant 1445917441931281
- Instagram « @eventys.paris » relié à cette Page
- Un jeton fonctionne déjà pour Instagram. Il ne faut PAS le casser.

OBJECTIF
Ajouter l'autorisation `pages_manage_posts` à l'application, puis générer un
nouveau jeton qui la contienne, en conservant la Page sélectionnée.

ÉTAPE 1 — Ajouter l'autorisation à l'application
1. Va sur https://developers.facebook.com/apps/1837815554329232/permissions/
   (si cette adresse ne s'ouvre pas : tableau de bord de l'app, puis
   « Autorisations et fonctionnalités » dans le menu de gauche)
2. Dans le champ de recherche, tape : pages_manage_posts
3. Sur la ligne trouvée, clique sur le bouton qui donne l'ACCÈS STANDARD
   (libellé possible : « Obtenir l'accès standard », « Ajouter », « Demander »)
4. IMPORTANT : ne demande JAMAIS l'« accès avancé » / « Advanced Access ».
   Cela déclencherait une procédure de vérification de plusieurs semaines
   dont je n'ai pas besoin.
5. Dis-moi ce qu'affiche la colonne de statut après ton clic.

ÉTAPE 2 — Générer un nouveau jeton
1. Va sur https://developers.facebook.com/tools/explorer/
2. Application Meta : « Eventys Publication »
3. Dans les autorisations, sélectionne ces HUIT entrées :
   instagram_basic
   instagram_content_publish
   instagram_manage_messages
   pages_show_list
   pages_read_engagement
   pages_manage_metadata
   pages_manage_posts
   business_management
4. Clique « Générer un token d'accès »

ÉTAPE 3 — L'écran à ne pas rater
Une fenêtre d'autorisation Facebook va s'ouvrir. Les cases y sont DÉCOCHÉES
par défaut, et c'est l'erreur qui nous a fait perdre beaucoup de temps la
dernière fois.

- Si un écran demande quelles Pages : COCHE « Eventys.paris »
- Si un écran demande quels comptes Instagram : COCHE « eventys.paris »
- Ne décoche aucune autorisation sur l'écran récapitulatif

Décris-moi ce que tu as coché AVANT de valider chaque écran.

ÉTAPE 4 — Allonger la durée du jeton
1. Clique le bouton d'information (ⓘ) à côté du jeton affiché
2. « Ouvrir dans l'outil d'access token »
3. En bas de page : « Étendre l'access token »
4. Si un mot de passe est demandé, ARRÊTE-TOI et préviens-moi : je le saisis
   moi-même, tu ne touches pas à mes identifiants
5. Un nouveau jeton apparaît en dessous

ÉTAPE 5 — Vérifier avant de me rendre la main
Dis-moi :
- la date d'expiration du nouveau jeton (elle doit être dans ~60 jours)
- la liste des autorisations qu'il porte : `pages_manage_posts` doit y figurer
- les Pages associées : « Eventys.paris » doit y figurer

Si `pages_manage_posts` n'apparaît pas, l'étape 1 n'a pas pris effet et il
faut y retourner.

CONSIGNE DE SÉCURITÉ
N'écris jamais le jeton ni un mot de passe dans ta réponse. Si Facebook
affiche une vérification de sécurité, une double authentification ou une
demande d'identité, arrête-toi et préviens-moi : je m'en occupe moi-même.

---
