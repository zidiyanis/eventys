/* Eventys — flux calendrier pour Apple Calendrier (abonnement .ics).
   GET /api/calendrier?t=<jeton secret>
   Le jeton est vérifié par la base (fonction evenements_ics) : sans le bon
   jeton, rien ne sort. Sens unique : l'app écrit, Apple lit. */
const CAT = require('../gestion/catalogue.js');

const SB_URL = 'https://qtktxkolgxytroblylae.supabase.co';
const SB_KEY = 'sb_publishable_Wf4Qc4XkVxI9-5fnFoRoVg_1Yir0Jlt';

const pad = n => String(n).padStart(2, '0');
const esc = s => String(s == null ? '' : s).replace(/\\/g, '\\\\').replace(/\r?\n/g, '\\n').replace(/([,;])/g, '\\$1');
const eur = n => Math.round(n).toLocaleString('fr-FR').replace(/\u202f|\u00a0/g, ' ') + ' €';

/* Plie les lignes à 75 octets comme le demande la norme iCalendar. */
function fold(line) {
  const out = [];
  let cur = '', bytes = 0;
  for (const ch of line) {
    const b = Buffer.byteLength(ch);
    if (bytes + b > 74) { out.push(cur); cur = ' ' + ch; bytes = 1 + b; }
    else { cur += ch; bytes += b; }
  }
  out.push(cur);
  return out.join('\r\n');
}
const dt = (iso, hhmm) => iso.replace(/-/g, '') + 'T' + (hhmm || '12:00').replace(':', '').slice(0, 4) + '00';
function addMin(iso, hhmm, m) {
  const [h, mi] = (hhmm || '12:00').split(':').map(Number);
  const d = new Date(Date.UTC(+iso.slice(0, 4), +iso.slice(5, 7) - 1, +iso.slice(8, 10), h, mi + m));
  return d.getUTCFullYear() + pad(d.getUTCMonth() + 1) + pad(d.getUTCDate()) + 'T' + pad(d.getUTCHours()) + pad(d.getUTCMinutes()) + '00';
}

const TZ = [
  'BEGIN:VTIMEZONE', 'TZID:Europe/Paris',
  'BEGIN:DAYLIGHT', 'TZOFFSETFROM:+0100', 'TZOFFSETTO:+0200', 'TZNAME:CEST', 'DTSTART:19700329T020000', 'RRULE:FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU', 'END:DAYLIGHT',
  'BEGIN:STANDARD', 'TZOFFSETFROM:+0200', 'TZOFFSETTO:+0100', 'TZNAME:CET', 'DTSTART:19701025T030000', 'RRULE:FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU', 'END:STANDARD',
  'END:VTIMEZONE'
];

function build(data) {
  const price = k => {
    const it = CAT.items.find(i => i.k === k);
    if (!it) return 0;
    return k === 'chaise' && data.hiver ? CAT.hiverChaise : it.p;
  };
  const name = k => { const it = CAT.items.find(i => i.k === k); return it ? it.n : k; };
  const stamp = new Date().toISOString().replace(/[-:]/g, '').slice(0, 15) + 'Z';
  const L = ['BEGIN:VCALENDAR', 'VERSION:2.0', 'PRODID:-//Eventys//Gestion//FR', 'CALSCALE:GREGORIAN', 'METHOD:PUBLISH',
    'X-WR-CALNAME:Eventys', 'X-WR-TIMEZONE:Europe/Paris', 'REFRESH-INTERVAL;VALUE=DURATION:PT1H', 'X-PUBLISHED-TTL:PT1H', ...TZ];
  const marge = +data.marge || 10, charge = +data.charge || 30;
  for (const r of data.res || []) {
    const liv = r.mode === 'livraison';
    const items = r.items || {};
    const keys = Object.keys(items).filter(k => items[k] > 0);
    const loc = keys.reduce((t, k) => t + items[k] * price(k), 0);
    const total = Math.max(0, loc + (liv ? +r.liv || 0 : 0) - (+r.remise || 0));
    const reste = total - (+r.paye || 0);
    const lignes = keys.map(k => `${items[k]} × ${name(k)}`).join('\n');
    const trajet = liv ? (+r.trajet || 0) : 0;
    const base = [
      lignes,
      `Total ${eur(total)} · ${reste > 0 ? 'reste ' + eur(reste) : reste < 0 ? 'trop-perçu ' + eur(-reste) : 'soldé'}`,
      r.tel ? 'Tél. ' + r.tel : ''
    ].filter(Boolean).join('\n');
    const addr = liv ? (r.adr || r.ville || '') : 'Box Eventys, Soisy-sous-Montmorency';
    const ev = (suffix, titre, date, heure, alarme, desc) => {
      L.push('BEGIN:VEVENT', `UID:${r.id}-${suffix}@eventysparis.fr`, `DTSTAMP:${stamp}`,
        `DTSTART;TZID=Europe/Paris:${dt(date, heure)}`, `DTEND;TZID=Europe/Paris:${addMin(date, heure, 60)}`,
        fold(`SUMMARY:${esc(titre)}`), fold(`DESCRIPTION:${esc(desc)}`));
      if (addr) L.push(fold(`LOCATION:${esc(addr)}`));
      if (r.statut === 'terminee') L.push('STATUS:CONFIRMED', 'TRANSP:TRANSPARENT');
      else L.push('STATUS:CONFIRMED');
      if (alarme && r.statut !== 'terminee') {
        L.push('BEGIN:VALARM', 'ACTION:DISPLAY', fold(`DESCRIPTION:${esc(alarme.txt)}`), `TRIGGER:-PT${alarme.min}M`, 'END:VALARM');
      }
      L.push('END:VEVENT');
    };
    if (liv) {
      const avant = trajet + marge;
      ev('aller', `🚚 Livraison ${r.client}${r.ville ? ' · ' + r.ville : ''}`, r.date, r.heure,
        { min: avant + charge, txt: `Chargement au box pour ${r.client}` },
        `Départ à ${addMin(r.date, r.heure, -avant).slice(9, 11)}:${addMin(r.date, r.heure, -avant).slice(11, 13)} (trajet ${trajet} min + ${marge} min de marge)\n` + base);
      if (r.retour) ev('retour', `↩︎ Récupération ${r.client}${r.ville ? ' · ' + r.ville : ''}`, r.retour, r.heure_retour,
        { min: avant, txt: `Partir récupérer chez ${r.client}` }, base);
    } else {
      ev('aller', `📦 Retrait au box · ${r.client}`, r.date, r.heure, { min: 30, txt: `${r.client} passe au box` }, base);
      if (r.retour) ev('retour', `📦 Retour au box · ${r.client}`, r.retour, r.heure_retour, { min: 30, txt: `${r.client} rapporte le matériel` }, base);
    }
  }
  L.push('END:VCALENDAR');
  return L.join('\r\n') + '\r\n';
}

module.exports = async (req, res) => {
  const t = String((req.query && req.query.t) || '').slice(0, 200);
  res.setHeader('X-Robots-Tag', 'noindex, nofollow');
  res.setHeader('Cache-Control', 'private, no-store');
  if (!/^[a-f0-9]{32,128}$/.test(t)) { res.statusCode = 404; return res.end('Introuvable'); }
  try {
    const r = await fetch(`${SB_URL}/rest/v1/rpc/evenements_ics`, {
      method: 'POST',
      headers: { apikey: SB_KEY, Authorization: `Bearer ${SB_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ p_token: t })
    });
    if (!r.ok) { res.statusCode = 502; return res.end('Base indisponible'); }
    const data = await r.json();
    if (!data) { res.statusCode = 404; return res.end('Introuvable'); }
    res.setHeader('Content-Type', 'text/calendar; charset=utf-8');
    res.setHeader('Content-Disposition', 'inline; filename="eventys.ics"');
    res.statusCode = 200;
    return res.end(build(data));
  } catch (e) {
    res.statusCode = 500;
    return res.end('Erreur');
  }
};
module.exports.build = build;
