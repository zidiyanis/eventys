# -*- coding: utf-8 -*-
"""Repliques du Reel « 20 personnes a table ? 120 € » (2 novembre).

Voix JONATHAN uniquement (verrouillee). Accents obligatoires : ElevenLabs lit
litteralement ce qu'on lui donne. Les nombres sont ecrits en toutes lettres.
Aucun chiffre de stock, jamais « livraison comprise ».
"""
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RACINE, "voix"))
import generer as g  # noqa: E402

DOSSIER = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "_attente_2026-11-02", "voix", "JONATHAN")

g.SCRIPT = [
    "Vingt personnes à table ? Cent vingt euros de mobilier.",
    "Vingt chaises Napoléon : soixante euros.",
    "Deux tables de dix : vingt euros.",
    "Vingt couverts complets : quarante euros.",
    "Total : cent vingt euros.",
    "Je livre et je monte, selon votre zone.",
    "C'est pour quelle date ? Écrivez-moi.",
    "Et abonnez-vous, c'est gratuit. [blasé] Allez. On recommence.",
]

if __name__ == "__main__":
    d = g.genere("JONATHAN", g.VOIX["JONATHAN"], DOSSIER)
    print(f"{len(d)} repliques, {sum(d):.1f}s")
    print("  ".join(f"{x:.2f}" for x in d))
