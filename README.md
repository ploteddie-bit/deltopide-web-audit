# Deltopide Web Audit

Outil d'audit web professionnel couvrant SEO, GEO (Generative Engine Optimization), et CBOR-Web.
Disponible en **CLI Python** et **Extension Chrome**.

> Standard Deltopide v1.2 — Moteur Rust/WASM — 35 checks sur 4 piliers.

[![Version](https://img.shields.io/badge/version-1.2.0-00d4aa)](https://github.com/ploteddie-bit/web-audit-tool)
[![Rust](https://img.shields.io/badge/engine-Rust%2FWASM-orange)](https://github.com/ploteddie-bit/web-audit-tool/tree/master/audit-engine-rs)
[![Chrome](https://img.shields.io/badge/Chrome-Extension%20MV3-blue)](https://github.com/ploteddie-bit/web-audit-tool/tree/master/extension)
[![License](https://img.shields.io/badge/license-Proprietary-red)](LICENSE)

## Fonctionnalites

### 4 piliers d'audit

| Pilier | Checks | Domaine |
|--------|--------|---------|
| Fondations Techniques | 18 | SSR, sitemap, robots.txt, meta tags, OG, Schema.org, canonical, hreflang, Core Web Vitals (TTFB, FCP, LCP, CLS), favicon, HTTPS, viewport |
| Contenu & Autorite SEO | 10 | Volume texte, H1/H2, images alt, maillage interne, E-E-A-T, mentions legales, fraicheur, presence sociale |
| Visibilite IA (GEO) | 6 | Crawlers IA (GPTBot, ClaudeBot, etc.), structure pour LLM, donnees citables, schemas IA, llms.txt, titres-questions |
| SXG / CBOR-Web | 5 | index.cbor, Signed Exchanges, headers securite, CDN |

### Extension Chrome

- Audit en 1 clic depuis le popup
- Side panel avec vue detaillee
- Detection automatique sur chaque page
- Export JSON et CSV
- Systeme de licence + integrite SHA-256
- Score visuel par pilier avec barres animees
- Top 8 actions prioritaires classees par impact

### CLI Python

- Audit depuis le terminal
- Sortie JSON ou HTML
- Audit de multiples sites en une commande
- Integration CI/CD possible

## Installation

### Extension Chrome (recommande)

1. Telecharger la derniere release
2. Dezipper
3. Ouvrir `chrome://extensions/`
4. Activer le **Mode developpeur** (en haut a droite)
5. Cliquer **Charger l'extension non empaquetee**
6. Selectionner le dossier `extension/`
7. Entrer la cle de licence au premier lancement

### CLI Python

```bash
pip install requests beautifulsoup4 lxml
python3 audit.py https://example.com
```

## Usage

### Extension Chrome

1. Naviguer vers n'importe quel site
2. Cliquer sur l'icone Deltopide dans la barre Chrome
3. Cliquer **Lancer l'audit**
4. Consulter les scores + actions prioritaires
5. Ouvrir le **panneau lateral** pour la vue detaillee
6. **Exporter** en JSON ou CSV

### CLI Python

```bash
# Audit simple (sortie terminal)
python3 audit.py https://deltopide.fr

# Export JSON
python3 audit.py https://deltopide.fr --output rapport.json

# Export HTML
python3 audit.py https://deltopide.fr --format html --output rapport.html

# Audit multi-sites
python3 audit.py deltopide.fr example.com --output batch.json
```

## Securite

L'extension Chrome inclut :
- **Licence obligatoire** — activation par cle
- **Integrite SHA-256** — detection de toute modification des fichiers
- **CSP strict** — `script-src 'self'; object-src 'none'`
- **Rate limiting** — 30 audits/minute max
- **Expiration** — renouvellement annuel
- **Input validation** — sanitization de toutes les donnees DOM
- **Moteur Rust/WASM** — code compile en binaire, impossible a lire ou modifier

Voir [SECURITY.md](SECURITY.md) pour les details.

## Architecture

```
web-audit-tool/
  audit.py                     # CLI Python (standalone)
  build.sh                     # Build automatise (Rust → WASM → ZIP)
  audit-engine-rs/             # Source Rust du moteur d'audit
    Cargo.toml
    src/lib.rs                 # 550 lignes Rust — le cerveau
  extension/                   # Extension Chrome v1.2
    audit_engine_bg.wasm       # Binaire WASM compile (protege)
    audit_engine.js            # Glue WASM auto-generee
    background.js              # Wrapper JS (appelle WASM + Chrome API)
    content.js                 # Content script (analyse DOM)
    renderer.js                # Rendu partage (scores, checks, export)
    popup.html/js              # Popup (vue compacte)
    sidepanel.html/js          # Side panel (vue detaillee)
    styles.css                 # UI dark theme
    icons/                     # Icones Deltopide 16/32/48/128
  docs/
    INSTALL.md                 # Guide d'installation detaille
    USE-CASES.md               # Cas d'usage concrets
    CONTRIBUTING.md            # Guide de contribution
    FAQ.md                     # 15 questions frequentes
  store/
    description-fr.md          # Listing Chrome Web Store (FR)
    description-en.md          # Listing Chrome Web Store (EN)
    privacy-policy.md          # Politique de confidentialite
  .github/ISSUE_TEMPLATE/      # Templates bug report + feature request
  CHANGELOG.md
  SECURITY.md
  LICENSE
```

## Build

```bash
./build.sh
# → Compile Rust, genere WASM, minifie JS, cree dist/deltopide-audit-v1.2.0.zip
```

## Documentation

| Document | Contenu |
|----------|---------|
| [Installation](docs/INSTALL.md) | Guide pas-a-pas (Chrome + CLI + depannage) |
| [Cas d'usage](docs/USE-CASES.md) | 7 scenarios concrets (pre-prod, concurrentiel, GEO, monitoring...) |
| [FAQ](docs/FAQ.md) | 15 questions frequentes |
| [Contribution](docs/CONTRIBUTING.md) | Ajouter un check, modifier le moteur Rust, conventions |
| [Securite](SECURITY.md) | Modele de menace, licence, integrite, CSP |
| [Changelog](CHANGELOG.md) | Historique des versions |

## Standard Deltopide

Le **Standard Deltopide v1.2** definit 35 criteres d'audit web repartis sur 4 piliers, avec une attention particuliere a la **visibilite IA (GEO)** — un domaine encore peu couvert par les outils existants.

Le pilier GEO verifie si un site est optimise pour etre cite par les moteurs de reponse IA (ChatGPT, Perplexity, Gemini, Claude), en analysant :
- L'acces des crawlers IA via `robots.txt`
- La presence de `llms.txt`
- La structure du contenu (listes, tableaux, FAQ)
- Les titres sous forme de questions
- Les donnees citables (statistiques, citations, definitions)

## Licence

Voir [LICENSE](LICENSE).

---

*Created by [Deltopide](https://deltopide.com) (Eddie Plot & Claude) — 2026*
