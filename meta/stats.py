"""Releve les statistiques Instagram et Facebook.

    python H:/eventys/meta/stats.py            # les 10 dernieres publications
    python H:/eventys/meta/stats.py --jour     # bilan du jour, pour le Drive

Sert a repondre a une seule question : qu'est-ce qui marche ? Les chiffres
decident, pas les impressions. Et notamment la duree de visionnage, qui
dira si nos 35 secondes sont trop longues face aux 6-15 s des concurrents.
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

ICI = os.path.dirname(os.path.abspath(__file__))
IDENT = os.path.join(ICI, "identifiants.json")
API = "https://graph.facebook.com/v21.0"


def _ident():
    with open(IDENT, encoding="utf-8") as f:
        return json.load(f)


def _get(chemin, jeton, **p):
    p["access_token"] = jeton
    url = f"{API}/{chemin}?" + urllib.parse.urlencode(p)
    try:
        with urllib.request.urlopen(url, timeout=40) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        try:
            msg = json.loads(e.read().decode()).get("error", {}).get("message")
        except Exception:
            msg = str(e)
        return {"__e": msg}


def compte(ident):
    """Abonnes, portee, visites du profil sur 7 jours."""
    j = ident["page_token"]
    p = _get(ident["ig_user_id"], j,
             fields="username,followers_count,media_count")
    ins = _get(f"{ident['ig_user_id']}/insights", j,
               metric="reach,profile_views,accounts_engaged",
               period="day", metric_type="total_value")
    return p, ins


def publications(ident, limite=10):
    """Les dernieres publications avec leurs chiffres."""
    j = ident["page_token"]
    r = _get(f"{ident['ig_user_id']}/media", j, limit=limite,
             fields="id,caption,media_product_type,timestamp,permalink,"
                    "like_count,comments_count")
    sorties = []
    for m in r.get("data", []):
        mesures = ("views,reach,likes,comments,shares,saved,"
                   "ig_reels_avg_watch_time,ig_reels_video_view_total_time"
                   if m.get("media_product_type") == "REELS"
                   else "views,reach,likes,comments,shares,saved")
        ins = _get(f"{m['id']}/insights", j, metric=mesures)
        chiffres = {}
        for v in ins.get("data", []):
            val = v.get("values", [{}])[0].get("value")
            chiffres[v["name"]] = val
        m["chiffres"] = chiffres
        sorties.append(m)
    return sorties


def _ligne(m):
    c = m.get("chiffres", {})
    titre = (m.get("caption") or "").split("\n")[0][:40]
    duree = c.get("ig_reels_avg_watch_time")
    duree_txt = f"{duree/1000:.1f}s" if isinstance(duree, (int, float)) else "-"
    return (f"  {m.get('timestamp', '')[:10]}  "
            f"{m.get('media_product_type', ''):<8} "
            f"vues {str(c.get('views', '-')):>6}  "
            f"portee {str(c.get('reach', '-')):>6}  "
            f"J'aime {str(c.get('likes', m.get('like_count', '-'))):>4}  "
            f"enreg. {str(c.get('saved', '-')):>4}  "
            f"visionnage {duree_txt:>6}   {titre}")


def rapport(limite=10):
    ident = _ident()
    prof, ins = compte(ident)
    lignes = ["STATISTIQUES EVENTYS", "=" * 60, ""]
    if "__e" in prof:
        lignes.append("  compte : " + prof["__e"])
    else:
        lignes.append(f"  @{prof.get('username')} — "
                      f"{prof.get('followers_count')} abonnes, "
                      f"{prof.get('media_count')} publications")
    for v in (ins.get("data") or []):
        val = v.get("total_value", {}).get("value")
        if val is not None:
            lignes.append(f"  {v['name']} (24h) : {val}")
    lignes += ["", "DERNIERES PUBLICATIONS", "-" * 60]
    pubs = publications(ident, limite)
    if not pubs:
        lignes.append("  aucune publication trouvee")
    for m in pubs:
        lignes.append(_ligne(m))
    lignes += ["", "LIENS", "-" * 60]
    for m in pubs[:3]:
        lignes.append("  " + (m.get("permalink") or ""))
    return "\n".join(lignes)


if __name__ == "__main__":
    print(rapport(10 if "--jour" not in sys.argv else 5))
