# Changelog

## [1.1.0] - 2026-03-27

### Extension Chrome

#### Nouveaux checks (11)
- Canonical coherence (detecte domaine/URL incorrect)
- Hreflang (langues alternatives)
- Favicon (presence)
- First Contentful Paint (Core Web Vital, seuil 1.8s)
- Largest Contentful Paint (Core Web Vital, seuil 2.5s)
- Cumulative Layout Shift (Core Web Vital, seuil 0.1)
- Fraicheur du contenu (date derniere MAJ)
- Presence sociale (liens reseaux sociaux)
- llms.txt (fichier d'instructions pour LLM)
- Titres-questions (H2/H3 sous forme de question)
- Accessibilite basique (landmarks ARIA, skip link)

#### Securite
- Systeme de licence avec activation par cle
- Integrite SHA-256 des fichiers JS
- Content Security Policy strict
- Rate limiting (30 audits/minute)
- Expiration annuelle
- Input validation et sanitization
- Code obfusque (terser)

#### Ameliorations
- Export CSV (en plus du JSON)
- Timestamp dans le footer
- Content script auto-inject + injection a la demande
- Limites de donnees (headings 20 max, images 100 max, schemas 20 max)
- Logo Deltopide dans les icones

### CLI Python
- Pas de changement (v1.0)

## [1.0.0] - 2026-03-27

### Initial release
- CLI Python (`audit.py`) avec audit 4 piliers
- Extension Chrome avec popup + side panel
- 24 checks SEO/GEO/SXG-CBOR
- Export JSON
- Standard Deltopide v1.0
