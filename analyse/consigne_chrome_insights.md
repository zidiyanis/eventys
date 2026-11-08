# Consigne extension Chrome — ajouter la lecture des statistiques

Colle le bloc entre les tirets dans l'extension Claude, Facebook connecte.

---

Tu travailles dans mon navigateur sur mon compte Facebook. Mon application
Meta fonctionne deja pour publier sur Instagram et Facebook. Il manque UNE
autorisation pour pouvoir LIRE les statistiques des publications.

CONTEXTE DEJA EN PLACE - ne refais pas ces etapes
- Application Meta « Eventys Publication », identifiant 1837815554329232
- Page Facebook « Eventys.paris », identifiant 1445917441931281
- Instagram « @eventys.paris » relie a cette Page
- Un jeton permanent fonctionne deja. Il ne faut PAS le casser.

OBJECTIF
Ajouter l'autorisation `instagram_manage_insights`, puis generer un nouveau
jeton qui la contienne, en conservant la Page selectionnee.

ETAPE 1 - Ajouter l'autorisation
1. Va sur https://developers.facebook.com/apps/1837815554329232/permissions/
2. Cherche : instagram_manage_insights
3. Clique sur le bouton qui donne l'ACCES STANDARD
4. IMPORTANT : ne demande JAMAIS l'acces avance. Cela declencherait une
   procedure de verification de plusieurs semaines inutile ici.
5. Dis-moi ce qu'affiche la colonne de statut.

ETAPE 2 - Generer un nouveau jeton
1. Va sur https://developers.facebook.com/tools/explorer/
2. Application Meta : « Eventys Publication »
3. Selectionne ces NEUF autorisations :
   instagram_basic
   instagram_content_publish
   instagram_manage_messages
   instagram_manage_insights
   pages_show_list
   pages_read_engagement
   pages_manage_metadata
   pages_manage_posts
   business_management
4. Clique « Generer un token d'acces »
   (si le clic automatique n'ouvre pas la fenetre, demande-moi de cliquer :
   les navigateurs bloquent les pop-ups non humaines)

ETAPE 3 - L'ecran a ne pas rater
Les cases y sont DECOCHEES par defaut, c'est l'erreur qui nous a deja
coute du temps.
- Ecran des Pages : COCHE « Eventys.paris »
- Ecran Instagram : COCHE « eventys.paris »
- Ne decoche aucune autorisation sur le recapitulatif
Decris-moi ce que tu as coche AVANT de valider chaque ecran.

ETAPE 4 - Allonger la duree
1. Bouton d'information (i) a cote du jeton
2. « Ouvrir dans l'outil d'access token »
3. En bas : « Etendre l'access token »
4. Si un mot de passe est demande, ARRETE-TOI et previens-moi

ETAPE 5 - Verifier avant de me rendre la main
Dis-moi : la date d'expiration, la liste des autorisations portees par le
jeton (`instagram_manage_insights` doit y figurer), et les Pages associees.

SECURITE
N'ecris jamais le jeton ni un mot de passe dans ta reponse. Si Facebook
affiche une verification de securite, arrete-toi et previens-moi.
