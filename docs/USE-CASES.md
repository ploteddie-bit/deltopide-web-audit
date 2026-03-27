# Cas d'usage — Deltopide Web Audit

> 7 scenarios concrets d'utilisation de l'extension Chrome et du CLI Python.

---

## Table des matieres

1. [Audit avant mise en production](#1-audit-avant-mise-en-production)
2. [Audit concurrentiel](#2-audit-concurrentiel)
3. [Optimisation GEO / Visibilite IA](#3-optimisation-geo--visibilite-ia)
4. [Monitoring SEO continu](#4-monitoring-seo-continu)
5. [Audit CBOR-Web](#5-audit-cbor-web)
6. [Onboarding client en agence web](#6-onboarding-client-en-agence-web)
7. [Audit accessibilite de base](#7-audit-accessibilite-de-base)

---

## 1. Audit avant mise en production

### Objectif

Verifier qu'un site ou une page respecte les standards minimaux avant publication. Eviter les oublis classiques (meta manquantes, images sans alt, absence de sitemap).

### Procedure

1. Deployer le site en pre-production (staging ou localhost)
2. Ouvrir la page dans Chrome et lancer l'audit via l'extension
3. Consulter le panneau lateral pour la vue detaillee
4. Verifier que les scores atteignent les seuils minimaux

### Checklist de scores minimaux

| Pilier | Score minimum recommande | Points critiques |
|--------|--------------------------|-----------------|
| Fondations Techniques | **70%** | HTTPS, title, meta description, viewport, canonical, sitemap.xml, robots.txt |
| Contenu & Autorite SEO | **60%** | H1 unique, volume de texte > 300 mots, images avec alt, maillage interne |
| Visibilite IA (GEO) | **50%** | Crawlers IA autorises dans robots.txt, donnees structurees Schema.org |
| SXG / CBOR-Web | **Variable** | Non bloquant pour une premiere mise en production |

### Resultat attendu

Un rapport JSON ou CSV exportable, partage avec l'equipe de developpement pour corriger les points non conformes avant la mise en ligne.

---

## 2. Audit concurrentiel

### Objectif

Comparer votre site avec 3 a 5 concurrents directs pour identifier les ecarts de performance SEO, GEO et technique.

### Procedure avec le CLI Python (batch)

```bash
# Auditer 5 sites concurrents en une commande
python3 audit.py \
    monsite.fr \
    concurrent1.com \
    concurrent2.fr \
    concurrent3.com \
    concurrent4.es \
    --output audit-concurrentiel.json
```

### Procedure avec l'extension Chrome

1. Ouvrir chaque site concurrent dans un onglet
2. Lancer l'audit sur chaque onglet
3. Exporter chaque rapport en JSON
4. Comparer les scores par pilier

### Exploitation des resultats

| Donnee | Utilisation |
|--------|------------|
| Score global par pilier | Identifier les piliers ou vous etes en retard |
| Checks specifiques (Schema.org, llms.txt) | Reperer les bonnes pratiques des concurrents que vous n'appliquez pas |
| Volume de texte / maillage interne | Evaluer l'effort contenu necessaire |
| Crawlers IA autorises | Voir si les concurrents se positionnent deja pour la visibilite IA |

### Livrable type

Un tableau comparatif des scores sur les 4 piliers, accompagne des 8 actions prioritaires pour chaque site.

---

## 3. Optimisation GEO / Visibilite IA

### Objectif

Ameliorer la visibilite de votre site dans les moteurs de reponse IA (ChatGPT, Perplexity, Gemini, Claude). Le pilier GEO du Standard Deltopide audite 6 checks specifiques.

### Tableau d'actions par check GEO

| Check GEO | Statut possible | Action corrective |
|-----------|----------------|-------------------|
| **Crawlers IA dans robots.txt** | OK / ABSENT / A_CORRIGER | Ajouter les user-agents autorises : `GPTBot`, `ClaudeBot`, `Google-Extended`, `PerplexityBot`, `ChatGPT-User`. Ne pas bloquer via `Disallow` les bots que vous souhaitez laisser passer |
| **Structure pour LLM** | OK / A_CORRIGER | Structurer le contenu avec des listes (`<ul>`, `<ol>`), tableaux (`<table>`), blocs de citation (`<blockquote>`), listes de definition (`<dl>`) — les LLM extraient mieux les donnees structurees |
| **Donnees citables** | OK / ABSENT | Ajouter des chiffres, statistiques, definitions, citations attribuees. Les LLM privilegient les sources qui fournissent des donnees factuelles verifiables |
| **Schemas IA (Schema.org)** | OK / ABSENT | Ajouter des JSON-LD : `FAQPage`, `HowTo`, `Article`, `Organization`, `Product`. Enrichir avec `author`, `dateModified`, `aggregateRating` |
| **llms.txt** | OK / ABSENT | Creer un fichier `llms.txt` a la racine du site (equivalent de robots.txt pour les LLM). Decrire le site, son domaine d'expertise, les pages cles |
| **Titres-questions** | OK / ABSENT | Reformuler certains H2/H3 sous forme de questions ("Comment fonctionne X ?", "Qu'est-ce que Y ?"). Les moteurs IA matchent les requetes utilisateur avec les titres interrogatifs |

### Strategie recommandee

1. Lancer l'audit GEO via l'extension
2. Identifier les checks ABSENT ou A_CORRIGER
3. Appliquer les actions du tableau ci-dessus par ordre de priorite
4. Relancer l'audit pour verifier la progression
5. Viser un score GEO superieur a **70%** pour un bon positionnement IA

---

## 4. Monitoring SEO continu

### Objectif

Suivre l'evolution des scores SEO/GEO d'un site dans le temps grace au CLI Python, execute en tache planifiee (cron).

### Mise en place

```bash
# Script de monitoring hebdomadaire
#!/bin/bash
# /home/user/scripts/audit-hebdo.sh

DATE=$(date +%Y-%m-%d)
SITE="monsite.fr"
OUTPUT_DIR="/home/user/audits"

mkdir -p "$OUTPUT_DIR"

python3 /chemin/vers/audit.py "https://$SITE" \
    --output "$OUTPUT_DIR/audit-$SITE-$DATE.json"
```

### Crontab (execution chaque lundi a 8h)

```cron
0 8 * * 1 /home/user/scripts/audit-hebdo.sh
```

### Exploitation

- Comparer les fichiers JSON semaine apres semaine
- Detecter les regressions (score qui baisse apres un deploiement)
- Suivre la progression apres des optimisations
- Alerter en cas de chute brutale (sitemap supprime, robots.txt bloquant, etc.)

### Multi-sites

```bash
# Auditer un portefeuille de sites
for site in monsite.fr client1.com client2.es; do
    python3 audit.py "https://$site" \
        --output "$OUTPUT_DIR/audit-$site-$DATE.json"
done
```

---

## 5. Audit CBOR-Web

### Objectif

Verifier la conformite d'un site au standard CBOR-Web : presence d'un `index.cbor`, support des Signed Exchanges (SXG), headers de securite, et integration CDN.

### Ce que verifie le pilier SXG / CBOR-Web

| Check | Description | Critere |
|-------|------------|---------|
| **index.cbor** | Presence d'un fichier `index.cbor` a la racine du site | Requete `GET /index.cbor` — reponse 200 avec contenu CBOR valide |
| **Signed Exchanges** | Support SXG pour la distribution signee de contenu | Headers `Accept: application/signed-exchange;v=b3` |
| **Headers de securite** | Presence des headers de securite essentiels | `Content-Security-Policy`, `Strict-Transport-Security`, `X-Content-Type-Options`, `X-Frame-Options` |
| **CDN** | Distribution via un CDN pour les performances | Detection de headers CDN (Cloudflare, Fastly, CloudFront, etc.) |
| **HTTPS strict** | Connexion securisee | Protocole HTTPS actif, pas de mixed content |

### Procedure

1. Publier le `index.cbor` a la racine du site via la Publisher API cbor-web.com
2. Lancer l'audit avec l'extension Deltopide
3. Ouvrir le panneau lateral et consulter le pilier "SXG / CBOR-Web"
4. Verifier chaque check individuellement

### Pourquoi un score SXG/CBOR bas est normal

La plupart des sites web actuels n'implementent pas encore CBOR-Web ni les Signed Exchanges. Un score bas sur ce pilier n'est pas un probleme critique — il indique un potentiel d'amelioration pour le futur du web.

### Cas avance : validation complete

Pour les sites deja conformes CBOR-Web, utiliser l'outil complementaire `cbor-crawl` :

```bash
# Inspecter un index.cbor
cbor-crawl inspect https://monsite.fr/index.cbor

# Verifier la signature
cbor-crawl verify https://monsite.fr/index.cbor
```

---

## 6. Onboarding client en agence web

### Objectif

Realiser un etat des lieux rapide du site d'un prospect ou nouveau client, et produire un rapport professionnel pour justifier un devis d'optimisation.

### Procedure (5 minutes)

1. Ouvrir le site du client dans Chrome
2. Lancer l'audit Deltopide (1 clic)
3. Ouvrir le panneau lateral pour la vue complete
4. Exporter le rapport en **JSON** et/ou **CSV**
5. Presenter les resultats au client

### Ce que revele l'audit

| Pilier | Questions auxquelles l'audit repond |
|--------|-------------------------------------|
| Fondations Techniques | Le site est-il correctement indexable ? Les meta tags sont-elles en place ? Le temps de chargement est-il acceptable (Core Web Vitals) ? |
| Contenu & Autorite SEO | Le contenu est-il suffisant ? Les images sont-elles optimisees (alt) ? Y a-t-il un maillage interne ? Les signaux E-E-A-T sont-ils presents ? |
| Visibilite IA (GEO) | Le site est-il visible pour les moteurs de reponse IA ? Les crawlers IA sont-ils autorises ? |
| SXG / CBOR-Web | Le site est-il conforme aux standards emergents ? |

### Construction du devis

Utiliser le **Top 8 des actions prioritaires** (affiche automatiquement par l'extension) pour structurer le devis :

1. Actions critiques (ABSENT) = interventions prioritaires
2. Actions a ameliorer (A_CORRIGER) = optimisations secondaires
3. Score cible par pilier = objectif mesurable pour le client

### Rapport client

Le JSON exporte contient toutes les donnees necessaires pour generer un rapport PDF personnalise. Chaque check inclut :
- Nom du check
- Pilier d'appartenance
- Statut (OK / A_CORRIGER / ABSENT)
- Valeur mesuree
- Seuil attendu

---

## 7. Audit accessibilite de base

### Objectif

Verifier les fondamentaux d'accessibilite web detectables par analyse statique du DOM. L'extension Deltopide ne remplace pas un audit WCAG complet mais couvre les bases.

### Checks d'accessibilite inclus

| Check | Ce qu'il verifie | Critere |
|-------|------------------|---------|
| **Attribut `lang`** | La langue de la page est declaree | `<html lang="fr">` present et non vide |
| **Viewport** | La page est responsive | `<meta name="viewport" ...>` present avec `width=device-width` |
| **Images sans alt** | Toutes les images ont un texte alternatif | Ratio images avec alt / images totales |
| **Landmarks ARIA** | La page utilise des regions ARIA | Presence de `role="main"`, `role="navigation"`, `<main>`, `<nav>`, `<header>`, `<footer>` |
| **Skip link** | Un lien d'evitement est present | Lien vers `#main`, `#content` ou similaire en debut de page |

### Procedure

1. Ouvrir la page a auditer
2. Lancer l'audit Deltopide
3. Consulter le pilier **Fondations Techniques** pour `lang`, `viewport`, `images alt`
4. Consulter le pilier **Contenu & Autorite SEO** pour le check accessibilite (landmarks, skip link)

### Limites

L'audit Deltopide detecte les problemes d'accessibilite **statiques** visibles dans le DOM. Il ne couvre pas :
- Les contrastes de couleur
- La navigation au clavier
- La compatibilite avec les lecteurs d'ecran
- Les tests WCAG 2.1 AA/AAA complets

Pour un audit accessibilite complet, combiner Deltopide avec des outils specialises (axe, WAVE, Pa11y).

### Actions correctives typiques

| Probleme detecte | Correction |
|-------------------|-----------|
| `lang` absent | Ajouter `lang="fr"` (ou la langue appropriee) sur `<html>` |
| `viewport` absent | Ajouter `<meta name="viewport" content="width=device-width, initial-scale=1">` |
| Images sans alt | Ajouter un `alt` descriptif a chaque `<img>`. Utiliser `alt=""` pour les images decoratives |
| Pas de landmarks ARIA | Structurer la page avec `<header>`, `<main>`, `<nav>`, `<footer>` |
| Pas de skip link | Ajouter `<a href="#main" class="skip-link">Aller au contenu</a>` en debut de page |

---

*Deltopide Web Audit — Eddie Plot, Deltopide SL — 2026*
