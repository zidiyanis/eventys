# Magic MCP (21st.dev) — ce qu'il faut pour l'activer

Magic MCP est un serveur qui génère des composants d'interface à la demande.
Je ne peux pas l'installer complètement à ta place : **il demande une clé
d'API personnelle**, et la session où je travaille ne peut pas ouvrir la page
de connexion.

## Les deux étapes, de ton côté

1. Va sur **https://21st.dev/magic/console**, connecte-toi et crée une clé
   d'API (c'est gratuit jusqu'à un certain nombre de générations).
2. Dans un terminal, depuis `H:\eventys` :

```
claude mcp add magic -- npx -y @21st-dev/magic@latest API_KEY=ta_cle_ici
```

Puis `/mcp` dans Claude Code pour vérifier que `magic` est bien connecté.

## Mon avis, maintenant que le site est fait

Le site d'Eventys est en HTML/CSS/JS sans framework, et sa charte (crème,
bordeaux, Bodoni, photos plein cadre) est déjà posée. Magic MCP génère
surtout des composants **React + Tailwind** très « produit SaaS » : utilisés
tels quels ici, ils casseraient la direction artistique.

Là où il serait vraiment utile :
- si un jour tu passes le site sous React/Next.js,
- ou pour un outil interne (tableau de bord des demandes, suivi du stock),
  où un composant standard fait gagner du temps sans toucher à l'image de
  la marque.

Dis-moi si tu veux qu'on aille dans cette direction, je m'en servirai à ce
moment-là.
