"""Configuration Meta en une seule commande, sans jamais taper de secret ailleurs.

    python H:/eventys/meta/demarrer.py

Le script DEMANDE les valeurs une par une, directement dans le terminal.
Les secrets sont saisis en aveugle (rien ne s'affiche pendant la frappe), et
ne sont jamais reaffiches. Plus aucune commande a recopier, donc plus aucun
risque de coller un secret dans une conversation.
"""
import getpass
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
FICHIER = os.path.join(ICI, "identifiants.json")
API = "https://graph.facebook.com/v21.0"


def _get(chemin, **params):
    url = f"{API}/{chemin}?" + urllib.parse.urlencode(params)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        detail = json.loads(e.read().decode()).get("error", {})
        raise SystemExit("\nMeta a refuse la requete :\n  "
                         + detail.get("message", str(e))
                         + "\n\nRien n'a ete enregistre.")


def demande_app_id():
    while True:
        v = input("  Identifiant de l'app (visible, ~15 chiffres) : ").strip()
        if v.isdigit() and len(v) >= 10:
            return v
        print("  -> Ce doit etre une suite de chiffres. Reessaie.")


def demande_secret():
    print("\n  Cle secrete de l'app : 32 caracteres, chiffres et lettres a-f.")
    print("  Elle se trouve dans Parametres de l'app > General.")
    print("  CE N'EST PAS un mot de passe. Rien ne s'affichera pendant la frappe.")
    while True:
        v = getpass.getpass("  Cle secrete (saisie invisible) : ").strip()
        if re.fullmatch(r"[0-9a-fA-F]{32}", v):
            return v.lower()
        print(f"  -> Recu {len(v)} caractere(s). Attendu : 32 en hexadecimal.")
        print("     Si tu as saisi un mot de passe, ce n'est pas la bonne valeur.")


def demande_token():
    print("\n  Jeton d'acces genere dans l'Explorateur d'API Graph.")
    print("  Il commence par EAA et fait plusieurs centaines de caracteres.")
    while True:
        v = getpass.getpass("  Jeton (saisie invisible) : ").strip()
        if v.startswith("EAA") and len(v) > 100:
            return v
        print(f"  -> Recu {len(v)} caractere(s), debut '{v[:3]}'. Attendu : EAA… et long.")


def main():
    print("=" * 62)
    print(" Configuration Meta pour Eventys")
    print(" Les secrets saisis ici ne sortent pas de ce terminal.")
    print("=" * 62)

    app_id = demande_app_id()
    secret = demande_secret()
    court = demande_token()

    print("\n1/4  Echange contre un jeton longue duree…")
    long_terme = _get("oauth/access_token", grant_type="fb_exchange_token",
                      client_id=app_id, client_secret=secret,
                      fb_exchange_token=court)["access_token"]
    print("     ok")

    print("2/4  Recherche de la Page…")
    pages = _get("me/accounts", access_token=long_terme).get("data", [])
    if not pages:
        raise SystemExit("     AUCUNE Page trouvee.\n"
                         "     L'autorisation n'a pas inclus la Page Eventys.\n"
                         "     Regenere le jeton en cochant bien la Page.")
    for p in pages:
        print(f"     trouvee : {p['name']}  (id {p['id']})")
    page = pages[0]

    print("3/4  Recherche du compte Instagram lie…")
    info = _get(page["id"], fields="instagram_business_account",
                access_token=long_terme)
    ig = info.get("instagram_business_account")
    ig_id = None
    if ig:
        ig_id = ig["id"]
        prof = _get(ig_id, fields="username", access_token=long_terme)
        print(f"     trouve : @{prof.get('username')}  (id {ig_id})")
    else:
        print("     AUCUN compte Instagram lie a cette Page.")
        print("     A relier dans les parametres de la Page avant de publier.")

    print("4/4  Enregistrement…")
    with open(FICHIER, "w", encoding="utf-8") as f:
        json.dump({
            "app_id": app_id,
            "app_secret": secret,
            "page_id": page["id"],
            "page_nom": page["name"],
            "page_token": page["access_token"],
            "user_token_long": long_terme,
            "ig_user_id": ig_id,
        }, f, indent=2, ensure_ascii=False)
    try:
        os.chmod(FICHIER, 0o600)
    except OSError:
        pass
    print("     ecrit :", FICHIER)

    print("\nTermine. Ce fichier contient des secrets :")
    print("  - ne l'ouvre pas pendant un partage d'ecran")
    print("  - n'en fais jamais de capture")
    return 0


if __name__ == "__main__":
    sys.exit(main())
