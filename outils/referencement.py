"""Referencement : ecrit dans le site tout ce qui depend de l'adresse finale.

Tant que le site n'est pas en ligne, on ne connait pas son adresse. Ce script
la pose partout d'un coup, et il est rejouable autant de fois qu'on veut (si
l'adresse change, on relance avec la nouvelle).

    python outils/referencement.py https://eventys-paris.github.io/site/

Il fait quatre choses :
  1. index.html   : <link rel="canonical"> et <meta property="og:url">, plus
                    les images de partage en adresse absolue (WhatsApp et
                    Instagram refusent les chemins relatifs) ;
  2. robots.txt   : tout le monde peut lire, y compris les robots d'IA ;
  3. sitemap.xml  : la page et ses ancres principales ;
  4. llms.txt     : la fiche de l'activite en texte, pour les IA.

Il verifie aussi que les prix ecrits en dur dans index.html sont les memes que
dans assets/js/donnees.js, et il refuse d'ecrire s'ils ne collent pas.
"""

import re
import sys
from datetime import date
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- verification


def prix_donnees():
    """Les prix de donnees.js, dans l'ordre : [(nom, prix), ...]."""
    texte = (RACINE / "assets/js/donnees.js").read_text(encoding="utf-8")
    bloc = texte.split("materiel: [", 1)[1].split("\n  ],", 1)[0]
    return re.findall(r'nom: "([^"]+)", prix: (\d+)', bloc)


def verifie_prix(html):
    """Chaque prix de donnees.js doit apparaitre dans le HTML statique."""
    liste = html.split('id="liste-materiel"', 1)[1].split("</ul>", 1)[0]
    ennuis = []
    for nom, prix in prix_donnees():
        court = nom.split(" ")[0]
        if court not in liste:
            ennuis.append("article absent du HTML : " + nom)
        elif prix + " &euro;" not in liste and prix + " €" not in liste:
            ennuis.append("prix %s manquant pour %s" % (prix, nom))
    return ennuis


# ------------------------------------------------------------------- index.html

CANON = '<link rel="canonical" href="%s">'
OGURL = '<meta property="og:url" content="%s">'


def fais_index(url):
    f = RACINE / "index.html"
    html = f.read_text(encoding="utf-8")

    ennuis = verifie_prix(html)
    if ennuis:
        print("STOP, les prix ne collent pas entre donnees.js et index.html :")
        for e in ennuis:
            print("  -", e)
        sys.exit(1)

    # on enleve d'abord les anciennes lignes, pour pouvoir rejouer le script
    html = re.sub(r'\n<link rel="canonical"[^>]*>', "", html)
    html = re.sub(r'\n<meta property="og:url"[^>]*>', "", html)

    html = html.replace(
        '<title>',
        CANON % url + "\n" + OGURL % url + "\n<title>", 1)

    # images de partage en absolu
    html = re.sub(r'(content=")(assets/img/)', lambda m: m.group(1) + url + m.group(2), html)
    # et dans les donnees structurees
    html = re.sub(r'("(?:image|logo)": ")(assets/img/)',
                  lambda m: m.group(1) + url + m.group(2), html)
    # l'identifiant de la fiche entreprise : en absolu, il sert d'identite
    # stable pour Google (les deux occurrences, la fiche et le renvoi).
    html = html.replace('"@id": "#eventys"', '"@id": "%s#eventys"' % url)

    f.write_text(html, encoding="utf-8")
    print("index.html : canonical, og:url et images absolues ->", url)


# ------------------------------------------------------------------- robots.txt

ROBOTS = """# Eventys - tout le monde peut lire le site.

User-agent: *
Allow: /

# Robots d'IA : explicitement autorises, pour que le site puisse etre cite
# dans les reponses (ChatGPT, Claude, Perplexity, Gemini, Copilot).
User-agent: GPTBot
Allow: /
User-agent: OAI-SearchBot
Allow: /
User-agent: ChatGPT-User
Allow: /
User-agent: ClaudeBot
Allow: /
User-agent: Claude-Web
Allow: /
User-agent: anthropic-ai
Allow: /
User-agent: PerplexityBot
Allow: /
User-agent: Google-Extended
Allow: /
User-agent: Applebot-Extended
Allow: /
User-agent: Bingbot
Allow: /

Sitemap: {url}sitemap.xml
"""

# ------------------------------------------------------------------ sitemap.xml

SITEMAP = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>{url}</loc>
    <lastmod>{jour}</lastmod>
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
</urlset>
"""

# --------------------------------------------------------------------- llms.txt

LLMS = """# Eventys

> Location de mobilier et de decoration d'evenement en Ile-de-France, par une
> seule personne : Yanis prepare, charge, livre, monte sur place et reprend le
> materiel apres l'evenement.

Site : {url}
Devis : par WhatsApp au +33 7 83 82 56 38, depuis le composeur de la page.
Depart du materiel : box a Soisy-sous-Montmorency (95230), Val-d'Oise.
Zone desservie : toute l'Ile-de-France (75, 77, 78, 91, 92, 93, 94, 95).
Reseaux : https://www.instagram.com/eventys.paris/ , https://www.tiktok.com/@eventys.paris

## Tarifs (par piece, pour la duree de l'evenement)

- Chaise Napoleon blanche : 3 EUR la piece (2 EUR en hiver)
- Table ronde 120 cm de diametre, 8 a 10 personnes : 10 EUR
- Table rectangulaire 70x180 cm, 8 a 10 personnes : 10 EUR
- Mange-debout 80x110 cm : 7 EUR
- Arche doree, ronde ou rectangulaire : 40 EUR
- Kit vaisselle (deux assiettes, un verre, les couverts dores) : 2 EUR par personne
- Nappe blanche : 9 EUR

Livraison : tarif selon la zone, chiffre dans le devis. Retrait au box possible.
Montage sur place : compris.

## Stock disponible

100 chaises Napoleon, 10 tables rectangulaires, 8 tables rondes, 2 arches
dorees, 75 kits vaisselle.

## Pour quels evenements

Mariages, fiancailles, anniversaires, baptemes, iftar du Ramadan et Aid, repas
de Noel, fetes de famille.

## Comment ca se passe

1. Le client indique le nombre de personnes sur le site ; la selection se
   remplit (une chaise et un kit par personne, une table et une nappe pour neuf).
2. Il envoie le message WhatsApp pre-rempli avec sa date et sa ville.
3. Le devis part en retour, livraison comprise. Rien n'est bloque avant accord.
"""


def fais_fichiers(url):
    (RACINE / "robots.txt").write_text(ROBOTS.format(url=url), encoding="utf-8")
    (RACINE / "sitemap.xml").write_text(
        SITEMAP.format(url=url, jour=date.today().isoformat()), encoding="utf-8")
    (RACINE / "llms.txt").write_text(LLMS.format(url=url), encoding="utf-8")
    print("robots.txt, sitemap.xml et llms.txt ecrits")


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    url = sys.argv[1]
    if not url.startswith("http"):
        print("Donne une adresse complete, qui commence par https://")
        sys.exit(1)
    if not url.endswith("/"):
        url += "/"
    fais_index(url)
    fais_fichiers(url)
    print("\nFait. Prochaine etape : deposer le site, puis declarer l'adresse")
    print("dans Google Search Console et sur la fiche Google Business Profile.")


if __name__ == "__main__":
    main()
