# Consigne à coller dans l'extension Claude pour Chrome

Copie tout le bloc ci-dessous (entre les lignes de tirets) et colle-le dans
l'extension Claude de ton navigateur, avec Facebook déjà connecté.

---

Tu travailles dans mon navigateur, sur mon compte Facebook, pour configurer
l'accès API d'une application que j'ai créée. Suis les étapes dans l'ordre et
arrête-toi en me prévenant si un écran ne correspond pas à la description.

CONTEXTE
- Application Meta : « Eventys Publication », identifiant 1837815554329232
- Portefeuille business : « Eventys »
- Page Facebook : « Eventys »
- Compte Instagram professionnel : « eventys.paris »

PROBLÈME À CORRIGER
Une première autorisation a été accordée sans sélectionner ni la Page ni le
compte Instagram. Le jeton obtenu a donc tous les droits mais sur aucun objet.
Facebook mémorise ce choix : il faut d'abord supprimer l'autorisation, sinon
les écrans de sélection ne réapparaîtront pas.

ÉTAPE 1 — Supprimer l'autorisation existante
1. Va sur https://www.facebook.com/settings?tab=applications
2. Trouve « Eventys Publication » dans la liste
3. Ouvre-la et clique sur Supprimer, puis confirme
4. Dis-moi si tu ne la trouves pas : cela voudrait dire qu'elle est déjà
   absente, et tu peux passer à l'étape suivante

ÉTAPE 2 — Vérifier que la Page existe vraiment
1. Va sur https://www.facebook.com/pages/?category=your_pages
2. Dis-moi le nom exact des Pages que tu vois
3. S'il n'y a aucune Page, ARRÊTE-TOI et préviens-moi : il faudra la créer
   avant de continuer

ÉTAPE 3 — Vérifier la liaison Instagram
1. Ouvre la Page Eventys, puis ses Paramètres
2. Cherche « Comptes liés » ou « Linked accounts »
3. Dis-moi si un compte Instagram y est relié, et lequel
4. S'il n'y en a aucun, relie « eventys.paris » et dis-le-moi

ÉTAPE 4 — Générer le jeton
1. Va sur https://developers.facebook.com/tools/explorer/
2. Dans « Application Meta » à droite, choisis « Eventys Publication »
3. Dans « Autorisations », sélectionne exactement ces sept entrées :
   instagram_basic
   instagram_content_publish
   instagram_manage_messages
   pages_show_list
   pages_read_engagement
   pages_manage_metadata
   business_management
4. Clique sur « Générer un token d'accès »

ÉTAPE 5 — L'étape critique, à ne pas précipiter
Une fenêtre Facebook s'ouvre et enchaîne plusieurs écrans. Sur chacun, les
cases sont DÉCOCHÉES par défaut. C'est ici que l'erreur précédente a eu lieu.

- Écran du portefeuille business : sélectionne « Eventys »
- Écran « Quelles Pages ? » : COCHE la Page « Eventys »
- Écran « Quels comptes Instagram ? » : COCHE « eventys.paris »
- Écran récapitulatif des autorisations : laisse tout activé, ne décoche rien

Avant de valider chaque écran, décris-moi ce que tu as coché.

ÉTAPE 6 — Allonger la durée du jeton
1. De retour dans l'Explorateur, clique sur le bouton d'information (ⓘ) à
   côté du jeton affiché
2. Clique sur « Ouvrir dans l'outil d'access token »
3. En bas de la page, clique sur « Étendre l'access token »
4. Saisis le mot de passe Facebook si demandé
5. Un nouveau jeton apparaît en dessous : c'est celui qui dure 60 jours

ÉTAPE 7 — Vérifier le résultat avant de me le donner
Sur cette même page d'outil de jeton, vérifie et dis-moi :
- la date d'expiration (elle doit être dans environ 60 jours)
- la ligne de l'identifiant de l'app
- et surtout : y a-t-il une section qui liste des Pages ou des comptes
  Instagram ? Si oui, dis-moi lesquels.

Si aucune Page n'apparaît, l'étape 5 a échoué et il faut tout reprendre à
l'étape 1.

CONSIGNE DE SÉCURITÉ
N'écris jamais le jeton ni le mot de passe dans ta réponse. Dis-moi seulement
que c'est fait, sa date d'expiration, et les Pages qui y sont associées. Je
viendrai copier le jeton moi-même sur l'écran.

---
