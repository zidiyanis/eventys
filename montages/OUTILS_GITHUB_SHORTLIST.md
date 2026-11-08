Written for : Yanis, pour choisir ce qu'on installe (rien n'est installé à ce stade).

# Shortlist d'outils trouvés sur awesome-claude-video-skills

Source : https://github.com/zhuyansen/awesome-claude-video-skills (commit c8b59c5, 6 oct. 2026). Le dépôt est une **liste de liens**, sans code exécutable. Chaque projet listé doit être installé séparément. Les notes « SAFE » et « CAUTION » viennent d'un site tiers (agentskillshub.top) qui a noté chaque dépôt : **je ne les ai pas vérifiés moi-même**.

## Règle avant toute installation
Les skills peuvent lancer des commandes sur ton ordinateur. Avant d'installer, je lis le code du projet, je te donne la liste des dépendances (Python, Node, modèles, clés API), et tu valides. Ça suit ta règle : pas d'installation sans accord, et les lourdes sur H:.

## Candidats pour notre montage

| Projet | ★ | Ce qu'il fait | Pertinence | Point d'attention |
|---|---:|---|---|---|
| [HyperFrames](https://github.com/heygen-com/hyperframes) (heygen-com) | 57,7k | Rend du HTML/CSS en MP4 | **Forte** : on pourrait remplacer mes cartes Pillow par du HTML, avec la police Bodoni et l'interlettrage natifs | Outil lourd (Node) |
| [ai-video-editing-skill](https://github.com/znyupup/ai-video-editing-skill) (znyupup) | 142 | Montage automatique de vlog : ffmpeg + Whisper + analyse d'image | **Forte** pour le Vlog et les coupes automatiques | Whisper est lourd, et l'analyse d'image demande une clé API payante |
| [vertical-video-editing-skill](https://github.com/adriiita/vertical-video-editing-skill) (adriiita) | 10 | Vidéo verticale 9:16 avec HyperFrames | Moyenne : même pile que HyperFrames | Petit projet |
| [kinetic-editorial-skill](https://github.com/ouerf-man/kinetic-editorial-skill) (ouerf-man) | 9 | Sous-titres animés mot par mot en 9:16 | Moyenne, si on ajoute une voix | Petit projet |
| [video-editor-agent](https://github.com/krusemediallc/video-editor-agent) (krusemediallc) | 24 | Montage motion graphics avec voix ElevenLabs | Faible : la voix synthétique n'est pas le but | Clé ElevenLabs payante |
| [tiktok-video-skills](https://github.com/iart-ai/tiktok-video-skills) (iart-ai) | 13 | Reels et TikTok « qui arrêtent le swipe » | Moyenne : méthode plus que code | À lire avant d'installer |

## À éviter
- **CAUTION** (notes du site tiers) : `argus-metis/hermes-video-editing`, `Dancan254/voiceover-video-skill`, `ops120/video-recap-skills-plus`.
- Les plugins **Adobe Premiere et After Effects** : il faut le logiciel Adobe payant.
- Les projets **en chinois ou russe uniquement** : pas de documentation pour nous.

## Ma recommandation
1. **HyperFrames** pour les cartes de texte. Il rend exactement ta DA (police, interlettrage, bicolore) sans passer par Pillow. Je le teste d'abord sur une seule carte, en installant sur H: si tu valides.
2. **ai-video-editing-skill** plus tard, pour le Vlog, seulement si tu acceptes Whisper et une clé API.

Dis-moi lequel tu veux que je regarde en détail. Je ne télécharge rien d'autre tant que tu n'as pas validé.
