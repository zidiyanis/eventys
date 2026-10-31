/* Eventys — le site. Pas de bibliothèque, pas d'étape de compilation :
   on ouvre index.html et ça marche.

   Refonte du 2026-10-22 : une seule liste de prix, qui sert aussi de
   formulaire ; le devis tient en trois gestes et se trouve en haut de page.

   1. on fabrique les sections à partir de donnees.js ;
   2. on tient la sélection du visiteur et on en écrit le message WhatsApp ;
   3. on anime : titre masqué, entrées au défilement. */

(function () {
  "use strict";

  const $ = (s, r) => (r || document).querySelector(s);
  const $$ = (s, r) => Array.from((r || document).querySelectorAll(s));
  const euros = (n) => n.toLocaleString("fr-FR") + " €";
  const sobre = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------------------------------------------------------------
     L'état. Sauvegardé dans le navigateur : un visiteur qui revient
     retrouve sa sélection.
     --------------------------------------------------------------- */
  let etat = { qte: {}, invites: 80 };
  try {
    const garde = localStorage.getItem("eventys-selection");
    if (garde) etat = Object.assign(etat, JSON.parse(garde));
  } catch (e) { /* navigation privée : on continue sans mémoire */ }

  function enregistre() {
    try { localStorage.setItem("eventys-selection", JSON.stringify(etat)); } catch (e) {}
  }

  const qte = (id) => etat.qte[id] || 0;
  const total = () => EVENTYS.materiel.reduce((s, a) => s + qte(a.id) * a.prix, 0);

  /* =========================================================
     1. L'ESSENTIEL
     ========================================================= */
  $("#essentiel").innerHTML = EVENTYS.essentiel.map((e) =>
    '<li class="entre"><h2>' + e.titre + '</h2><p>' + e.texte + '</p></li>').join("");

  /* =========================================================
     2. LE DEVIS — trois gestes
     ========================================================= */
  const tailles = $("#tailles");
  EVENTYS.tailles.forEach((n) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "taille";
    b.dataset.n = n;
    b.textContent = n + " pers.";
    b.addEventListener("click", () => { etat.invites = n; propose(); });
    tailles.appendChild(b);
  });

  const invites = $("#invites");
  invites.value = etat.invites;
  $("#invites-valeur").textContent = etat.invites;
  invites.addEventListener("input", () => {
    etat.invites = parseInt(invites.value, 10);
    propose();
  });

  /* une base simple : une chaise et un couvert par personne,
     une table et une nappe pour neuf. */
  function propose() {
    const n = etat.invites;
    const tables = Math.ceil(n / 9);
    etat.qte.chaise = n;
    etat.qte.kit = n;
    etat.qte.ronde = tables;
    etat.qte.nappe = tables;
    maj();
  }

  /* =========================================================
     3. LE MATÉRIEL ET LES PRIX — la seule liste de la page
     ========================================================= */
  $("#services").innerHTML = EVENTYS.services.map((s) =>
    '<li><span>' + s.nom + '</span><b>' + s.valeur + '</b></li>').join("");

  $("#liste-materiel").innerHTML = EVENTYS.materiel.map((a) =>
    '<li class="ligne entre">' +
      '<span class="ligne__nom">' + a.nom + '<i>' + a.texte + '</i></span>' +
      '<span class="ligne__prix">' + euros(a.prix) + '<i>' + a.unite + '</i></span>' +
      '<span class="compteur">' +
        '<button type="button" class="rond" data-moins="' + a.id + '" aria-label="Retirer une unité de ' + a.nom + '">−</button>' +
        '<input type="number" min="0" max="999" value="' + qte(a.id) + '" data-nb="' + a.id + '" aria-label="Quantité de ' + a.nom + '">' +
        '<button type="button" class="rond" data-plus="' + a.id + '" aria-label="Ajouter une unité de ' + a.nom + '">+</button>' +
      '</span>' +
    '</li>').join("");

  function change(id, delta, valeur) {
    const n = valeur !== undefined ? valeur : qte(id) + delta;
    etat.qte[id] = Math.max(0, Math.min(999, isNaN(n) ? 0 : n));
    maj();
  }
  document.addEventListener("click", (e) => {
    const plus = e.target.closest("[data-plus]");
    const moins = e.target.closest("[data-moins]");
    if (plus) change(plus.dataset.plus, 1);
    if (moins) change(moins.dataset.moins, -1);
  });
  document.addEventListener("input", (e) => {
    const champ = e.target.closest("[data-nb]");
    if (champ) change(champ.dataset.nb, 0, parseInt(champ.value, 10));
  });

  /* =========================================================
     4. LA BANDE — quatre emplacements qui changent chacun leur tour
     ========================================================= */
  const bande = $("#bande");
  bande.innerHTML = EVENTYS.bande.map((liste, i) =>
    '<div class="tuile" data-tuile="' + i + '">' +
      '<img class="tuile__a est-dessus" src="assets/img/' + liste[0].f + '" alt="' + liste[0].alt + '" loading="lazy">' +
      '<img class="tuile__b" alt="" aria-hidden="true">' +
    '</div>').join("");

  if (!sobre) {
    const rang = EVENTYS.bande.map(() => 0);
    $$(".tuile", bande).forEach((tuile, i) => {
      const liste = EVENTYS.bande[i];
      if (liste.length < 2) return;
      // chaque tuile part en décalé : une image change environ toutes les 1,5 s
      setTimeout(function boucle() {
        setInterval(function () {
          if (document.hidden || !visible(tuile)) return;
          rang[i] = (rang[i] + 1) % liste.length;
          const suivante = liste[rang[i]];
          const dessus = $(".est-dessus", tuile);
          const dessous = dessus.classList.contains("tuile__a") ? $(".tuile__b", tuile) : $(".tuile__a", tuile);
          const img = new Image();
          img.onload = function () {
            dessous.src = img.src;
            dessous.alt = suivante.alt;
            dessous.classList.add("est-dessus");
            dessus.classList.remove("est-dessus");
          };
          img.src = "assets/img/" + suivante.f;
        }, 6000);
      }, 1500 * i);
    });
  }

  function visible(el) {
    const r = el.getBoundingClientRect();
    return r.bottom > 0 && r.top < window.innerHeight;
  }

  /* =========================================================
     5. LE MESSAGE
     ========================================================= */
  function message() {
    const lignes = ["Bonjour Eventys, je prépare un événement pour " +
                    etat.invites + " personnes."];
    const choisis = EVENTYS.materiel.filter((a) => qte(a.id) > 0);
    if (choisis.length) {
      lignes.push("", "Ce que je voudrais :");
      choisis.forEach((a) => {
        lignes.push("- " + qte(a.id) + " x " + a.nom + " : " + euros(qte(a.id) * a.prix));
      });
      lignes.push("", "Total matériel (d'après votre site) : " + euros(total()));
    } else {
      lignes.push("", "Je n'ai pas encore choisi le matériel, pouvez-vous me conseiller ?");
    }
    lignes.push("", "Ma date et ma ville : ");
    return lignes.join("\n");
  }

  const envoyer = $("#envoyer");
  const recap = $("#recap-lignes");

  function lien() {
    const texte = encodeURIComponent(message());
    return EVENTYS.whatsapp
      ? "https://wa.me/" + EVENTYS.whatsapp + "?text=" + texte
      : "https://wa.me/?text=" + texte;
  }

  function maj() {
    EVENTYS.materiel.forEach((a) => {
      $$('[data-nb="' + a.id + '"]').forEach((champ) => {
        if (String(qte(a.id)) !== champ.value) champ.value = qte(a.id);
      });
    });
    $$(".taille").forEach((b) => {
      b.classList.toggle("est-choisi", Number(b.dataset.n) === etat.invites);
    });
    invites.value = etat.invites;
    $("#invites-valeur").textContent = etat.invites;

    const choisis = EVENTYS.materiel.filter((a) => qte(a.id) > 0);
    recap.innerHTML = choisis.length
      ? choisis.map((a) =>
          '<li><span>' + qte(a.id) + ' × ' + a.nom + '</span>' +
          '<b>' + euros(qte(a.id) * a.prix) + '</b></li>').join("")
      : '<li class="recap__vide">Choisissez un nombre de personnes&nbsp;: ' +
        'je remplis la sélection.</li>';

    $("#total").textContent = euros(total());
    envoyer.href = lien();
    $("#wa-pied").href = lien();
    enregistre();
  }

  /* sans numéro renseigné, le bouton ne peut pas joindre Yanis :
     on le dit, et on propose de copier le message. */
  if (!EVENTYS.whatsapp) {
    $("#copier").hidden = false;
    envoyer.addEventListener("click", (e) => {
      e.preventDefault();
      copie();
      alert("Le numéro WhatsApp n'est pas encore renseigné dans le site " +
            "(assets/js/donnees.js). Le message a été copié : collez-le dans WhatsApp.");
    });
  }

  function copie() {
    const texte = message();
    if (navigator.clipboard) {
      navigator.clipboard.writeText(texte).then(dis, replis);
    } else { replis(); }
    function replis() {
      const z = document.createElement("textarea");
      z.value = texte; document.body.appendChild(z); z.select();
      try { document.execCommand("copy"); dis(); } catch (err) {}
      document.body.removeChild(z);
    }
    function dis() {
      const b = $("#copier");
      b.textContent = "Message copié";
      setTimeout(() => { b.textContent = "Copier le message"; }, 1800);
    }
  }
  $("#copier").addEventListener("click", copie);

  if (!Object.keys(etat.qte).length) propose(); else maj();

  /* =========================================================
     6. LE MOUVEMENT
     ========================================================= */
  if (location.search.indexOf("anim=0") !== -1) document.body.classList.add("tout-visible");

  requestAnimationFrame(() => document.body.classList.add("pret"));

  function observeEntrees() {
    const cibles = $$(".entre");
    if (sobre || !("IntersectionObserver" in window)) {
      cibles.forEach((c) => c.classList.add("est-entre"));
      return;
    }
    const io = new IntersectionObserver((lignes) => {
      lignes.forEach((l) => {
        if (l.isIntersecting) { l.target.classList.add("est-entre"); io.unobserve(l.target); }
      });
    }, { rootMargin: "0px 0px -6% 0px", threshold: 0.08 });
    cibles.forEach((c) => io.observe(c));
  }
  observeEntrees();

  /* la vidéo de l'accroche ne tourne que lorsqu'on la voit */
  const video = $(".hero__media");
  const demarre = () => {
    if (!video.src) video.src = "assets/video/hero-table.mp4";
    const p = video.play();
    if (p && p.catch) p.catch(() => {});
  };
  if ("IntersectionObserver" in window) {
    new IntersectionObserver((l) => {
      l.forEach((x) => { if (x.isIntersecting) demarre(); else if (video.src) video.pause(); });
    }, { threshold: 0.25 }).observe(video);
  } else { demarre(); }

  /* la barre haute n'apparaît qu'une fois l'accroche passée */
  const barre = $("#barre-haute");
  const hero = $(".hero");
  let tourne = false;
  window.addEventListener("scroll", () => {
    if (tourne) return;
    tourne = true;
    requestAnimationFrame(() => {
      const y = window.scrollY;
      barre.classList.toggle("est-visible", y > window.innerHeight * 0.85);
      if (!sobre) hero.style.setProperty("--glisse", (Math.min(y, window.innerHeight) * 0.07).toFixed(1) + "px");
      tourne = false;
    });
  }, { passive: true });

  /* défilement doux sur les ancres */
  $$('a[href^="#"]').forEach((a) => {
    a.addEventListener("click", (e) => {
      const cible = document.getElementById(a.getAttribute("href").slice(1));
      if (!cible) return;
      e.preventDefault();
      cible.scrollIntoView({ behavior: sobre ? "auto" : "smooth", block: "start" });
      history.replaceState(null, "", a.getAttribute("href"));
    });
  });

})();
