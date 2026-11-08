# -*- coding: utf-8 -*-
"""Repliques du Reel « Livree ou a recuperer au box ? » (4 novembre).

Voix JONATHAN uniquement (verrouillee). Accents obligatoires : ElevenLabs lit
litteralement ce qu'on lui donne. Nombres en toutes lettres. Aucun chiffre de
stock, jamais « livraison comprise ».
"""
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "voix"))
import generer as g  # noqa: E402

DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "_attente_2026-11-04", "voix", "JONATHAN")

g.SCRIPT = [
    "Livrée ou au box ? La chaise Napoléon, trois euros.",
    "Vous la prenez au box, dans le Val-d'Oise.",
    "Ou je vous la livre, selon votre zone.",
    "Et je monte tout sur place.",
    "Table ronde, dix euros.",
    "Le couvert complet : deux euros.",
    "C'est pour quelle date ? Écrivez-moi.",
    "Et abonnez-vous, c'est gratuit. [blasé] Allez. On recommence.",
]

if __name__ == "__main__":
    d = g.genere("JONATHAN", g.VOIX["JONATHAN"], DOSSIER)
    print(f"{len(d)} repliques, {sum(d):.1f}s")
    print("  ".join(f"{x:.2f}" for x in d))
