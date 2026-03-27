# Foire aux questions — Deltopide Web Audit

> 15 questions/reponses sur l'extension Chrome, le Standard Deltopide, et les concepts audites.

---

## Table des matieres

1. [Qu'est-ce que le Standard Deltopide ?](#1-quest-ce-que-le-standard-deltopide)
2. [Quelle difference avec Lighthouse ?](#2-quelle-difference-avec-lighthouse)
3. [Qu'est-ce que le GEO ?](#3-quest-ce-que-le-geo)
4. [Qu'est-ce que le CBOR-Web ?](#4-quest-ce-que-le-cbor-web)
5. [L'extension fonctionne-t-elle sur Firefox ?](#5-lextension-fonctionne-t-elle-sur-firefox)
6. [Mes donnees sont-elles envoyees a un serveur ?](#6-mes-donnees-sont-elles-envoyees-a-un-serveur)
7. [Comment obtenir une cle de licence ?](#7-comment-obtenir-une-cle-de-licence)
8. [L'extension ralentit-elle ma navigation ?](#8-lextension-ralentit-elle-ma-navigation)
9. [Puis-je auditer un site en local (localhost) ?](#9-puis-je-auditer-un-site-en-local-localhost)
10. [Pourquoi le score SXG/CBOR est-il toujours bas ?](#10-pourquoi-le-score-sxgcbor-est-il-toujours-bas)
11. [Comment ameliorer mon score GEO ?](#11-comment-ameliorer-mon-score-geo)
12. [L'extension fonctionne-t-elle sur mobile ?](#12-lextension-fonctionne-t-elle-sur-mobile)
13. [Puis-je utiliser l'outil en CI/CD ?](#13-puis-je-utiliser-loutil-en-cicd)
14. [Que signifie "moteur WASM" ?](#14-que-signifie-moteur-wasm)
15. [Comment mettre a jour l'extension ?](#15-comment-mettre-a-jour-lextension)

---

### 1. Qu'est-ce que le Standard Deltopide ?

Le **Standard Deltopide** est un referentiel d'audit web cree par Deltopide SL qui definit **35 criteres de qualite** repartis sur **4 piliers** :

| Pilier | Nombre de checks | Domaine |
|--------|-----------------|---------|
| Fondations Techniques | 18 | HTTPS, meta tags, canonical, sitemap, robots.txt, Core Web Vitals, favicon, hreflang, accessibilite de base |
| Contenu & Autorite SEO | 10 | Volume de texte, headings, images alt, maillage interne, signaux E-E-A-T, fraicheur, presence sociale |
| Visibilite IA (GEO) | 6 | Crawlers IA, structure LLM, donnees citables, schemas IA, llms.txt, titres-questions |
| SXG / CBOR-Web | 5 | index.cbor, Signed Exchanges, headers de securite, CDN |

La version actuelle est la **v1.2**. Le standard evolue regulierement pour integrer les nouvelles bonnes pratiques du web.

---

### 2. Quelle difference avec Lighthouse ?

| Critere | Lighthouse | Deltopide Web Audit |
|---------|-----------|---------------------|
| **Editeur** | Google | Deltopide SL |
| **Focus principal** | Performance, accessibilite, PWA, bonnes pratiques | SEO technique, visibilite IA (GEO), CBOR-Web |
| **Pilier GEO** | Absent | 6 checks dedies (crawlers IA, llms.txt, structure LLM) |
| **Pilier CBOR-Web** | Absent | 5 checks (index.cbor, SXG, headers securite) |
| **Core Web Vitals** | Mesure complete (lab data) | Detection basique (TTFB, FCP, LCP, CLS via Performance API) |
| **Moteur** | Node.js / Chrome DevTools Protocol | Rust/WASM (execution locale dans le navigateur) |
| **E-E-A-T** | Non audite | Checks sur about, contact, privacy, auteur, temoignages |
| **Execution** | Chrome DevTools ou CLI | Extension Chrome popup/panneau lateral + CLI Python |

En resume : Lighthouse excelle sur la performance et l'accessibilite. Deltopide excelle sur le SEO technique, la visibilite IA et les standards emergents (CBOR-Web). Les deux outils sont complementaires.

---

### 3. Qu'est-ce que le GEO ?

**GEO** signifie **Generative Engine Optimization**. C'est l'optimisation d'un site web pour etre cite et referencee par les moteurs de reponse generatifs bases sur l'IA :

- **ChatGPT** (OpenAI)
- **Perplexity**
- **Gemini** (Google)
- **Claude** (Anthropic)

Contrairement au SEO classique qui vise les pages de resultats de recherche, le GEO vise les **reponses generees** par ces outils IA. Un site bien optimise GEO a plus de chances d'etre cite comme source dans une reponse IA.

Les 6 checks GEO du Standard Deltopide verifient :
- Si les crawlers IA sont autorises dans `robots.txt`
- Si le contenu est structure de facon exploitable par un LLM (listes, tableaux, FAQ)
- Si le site fournit des donnees factuelles citables (statistiques, definitions)
- Si des schemas JSON-LD pertinents pour l'IA sont presents
- Si un fichier `llms.txt` existe a la racine
- Si certains titres sont formules sous forme de questions

---

### 4. Qu'est-ce que le CBOR-Web ?

**CBOR-Web** est un standard emergent qui propose une alternative binaire au HTML pour la distribution de contenu web. CBOR (Concise Binary Object Representation) est un format de serialisation binaire defini par la RFC 8949.

Dans le contexte du web, CBOR-Web definit :
- Un fichier **`index.cbor`** a la racine du site (equivalent binaire du `index.html`)
- L'utilisation de **Signed Exchanges (SXG)** pour la distribution signee et verifiable de contenu
- Une identite via **DNS TXT** records

Le pilier SXG/CBOR-Web de Deltopide verifie si un site adopte ces standards. Ce pilier est prospectif : la plupart des sites n'implementent pas encore CBOR-Web, ce qui est normal.

---

### 5. L'extension fonctionne-t-elle sur Firefox ?

**Non**. L'extension est developpee pour Google Chrome (Manifest V3) et utilise des API specifiques a Chrome :
- `chrome.sidePanel` (panneau lateral)
- `chrome.scripting` (injection de script)
- CSP avec `wasm-unsafe-eval` (execution WASM)

Les navigateurs bases sur Chromium (Brave, Edge, Opera) peuvent theoriquement charger l'extension, mais seul Chrome est officiellement supporte et teste.

Un portage vers Firefox n'est pas prevu a court terme en raison des differences d'API entre Manifest V3 Chrome et les WebExtensions Firefox.

---

### 6. Mes donnees sont-elles envoyees a un serveur ?

**Non, jamais.** L'extension fonctionne integralement en local :

- L'analyse DOM est faite par le **content script** dans le navigateur
- Le calcul des scores est fait par le **moteur Rust/WASM** dans le Service Worker
- Les requetes reseau (robots.txt, sitemap.xml, index.cbor) sont faites directement depuis le navigateur vers le site audite
- La cle de licence est stockee dans `chrome.storage.local` (jamais transmise)
- Aucun serveur tiers n'est contacte, aucun tracking, aucune telemetrie

Le code source est verifiable sur le depot GitHub.

---

### 7. Comment obtenir une cle de licence ?

Pour obtenir une cle de licence au format `DELTOPIDE-XXXX-XXXX-XXXX` :

- **Par email** : ecrire a contact@deltopide.com
- **Via le site** : [deltopide.fr](https://deltopide.fr)

La licence est valable **1 an** a compter de la date de build de l'extension. Le renouvellement se fait en telechargeant une nouvelle version de l'extension avec une date d'expiration mise a jour.

---

### 8. L'extension ralentit-elle ma navigation ?

**Non, l'impact est negligeable.** Voici pourquoi :

- Le **content script** est injecte a `document_idle` (apres le chargement complet de la page) et ne s'execute que lorsqu'un audit est lance
- Le **Service Worker** se charge au demarrage de Chrome mais reste inactif tant qu'aucun audit n'est demande
- Le **moteur WASM** est compile avec optimisation taille (`opt-level = "z"`) et pese quelques centaines de Ko
- Un **rate limiting** de 30 audits/minute empeche toute surcharge

L'extension ne modifie pas les pages visitees, n'injecte pas de CSS visible et ne fait aucune requete reseau en arriere-plan.

---

### 9. Puis-je auditer un site en local (localhost) ?

**Oui.** L'extension fonctionne sur `localhost` et sur toute URL accessible depuis le navigateur, y compris :

- `http://localhost:3000`
- `http://127.0.0.1:8080`
- `http://192.168.x.x` (reseau local)

Limitations sur localhost :
- Le check **HTTPS** sera marque ABSENT (normal en developpement local)
- Les checks **robots.txt** et **sitemap.xml** necessitent que ces fichiers soient servis par votre serveur local
- Le check **CDN** sera marque ABSENT

Cela reste utile pour valider les fondations techniques, le contenu et la structure avant un deploiement en production.

---

### 10. Pourquoi le score SXG/CBOR est-il toujours bas ?

C'est **normal et attendu**. Le pilier SXG/CBOR-Web audite des standards emergents que la grande majorite des sites web n'implementent pas encore :

- **index.cbor** : quasi aucun site ne publie de fichier CBOR a la racine
- **Signed Exchanges** : technologie encore experimentale, supportee uniquement par Chrome
- **Headers de securite** : seul check couramment implemente (`Content-Security-Policy`, `HSTS`)

Un score bas sur ce pilier **n'est pas un probleme**. Il reflete simplement que votre site n'a pas encore adopte ces standards. Concentrez vos efforts sur les 3 autres piliers en priorite.

Si vous souhaitez ameliorer ce score, commencez par les headers de securite (gain rapide) puis explorez CBOR-Web via la Publisher API cbor-web.com.

---

### 11. Comment ameliorer mon score GEO ?

Voici les actions classees par impact et facilite de mise en oeuvre :

| Priorite | Action | Effort |
|----------|--------|--------|
| 1 | Autoriser les crawlers IA dans `robots.txt` (GPTBot, ClaudeBot, etc.) | 5 minutes |
| 2 | Ajouter des schemas JSON-LD (`FAQPage`, `Article`, `Organization`) | 30 minutes |
| 3 | Creer un fichier `llms.txt` a la racine du site | 15 minutes |
| 4 | Reformuler certains H2/H3 en questions ("Comment...", "Qu'est-ce que...") | 1 heure |
| 5 | Structurer le contenu avec des listes, tableaux, definitions | 2 heures |
| 6 | Ajouter des donnees citables : chiffres, statistiques, definitions | Continu |

Un score GEO de **70% ou plus** positionne votre site favorablement pour etre cite par les moteurs de reponse IA.

Voir le cas d'usage detaille : [Optimisation GEO](USE-CASES.md#3-optimisation-geo--visibilite-ia).

---

### 12. L'extension fonctionne-t-elle sur mobile ?

**Non directement.** Chrome sur Android et iOS ne supporte pas les extensions.

Alternatives pour mobile :
- Utiliser le **CLI Python** depuis un serveur ou un terminal distant pour auditer des URLs mobiles
- Utiliser le **mode responsive** de Chrome Desktop (F12 → toggle device toolbar) pour simuler un mobile, puis lancer l'audit

L'extension analyse le DOM tel qu'il est rendu dans Chrome Desktop. Pour verifier le rendu mobile specifique, combiner avec les DevTools Chrome.

---

### 13. Puis-je utiliser l'outil en CI/CD ?

**Oui, via le CLI Python.** L'extension Chrome n'est pas adaptee a un pipeline CI/CD, mais `audit.py` l'est :

```bash
# Dans votre pipeline CI/CD
pip install requests beautifulsoup4 lxml

# Audit avec export JSON
python3 audit.py https://staging.monsite.fr --output audit-result.json

# Verifier un score minimum (exemple avec jq)
SCORE=$(cat audit-result.json | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(data['summary']['global_score'])
")

if [ "$SCORE" -lt 60 ]; then
    echo "Score global insuffisant : $SCORE/100"
    exit 1
fi
```

### Exemple d'integration GitHub Actions

```yaml
- name: Audit SEO
  run: |
    pip install requests beautifulsoup4 lxml
    python3 audit.py https://staging.monsite.fr --output audit.json
```

Le CLI Python ne necessite pas de licence et couvre les memes 4 piliers que l'extension.

---

### 14. Que signifie "moteur WASM" ?

**WASM** signifie **WebAssembly**. C'est un format d'execution binaire qui tourne dans le navigateur a des performances proches du code natif.

Le moteur d'audit Deltopide est ecrit en **Rust** et compile en WASM via `wasm-pack`. Cela permet :

| Avantage | Explication |
|----------|------------|
| **Performance** | Le calcul des 35 checks est quasi instantane (quelques millisecondes) |
| **Securite** | Le code Rust est memory-safe et le binaire WASM tourne dans un sandbox |
| **Portabilite** | Le meme binaire fonctionne sur Windows, macOS et Linux |
| **Integrite** | Le binaire WASM est verifie par hash SHA-256 a chaque audit |

L'architecture est la suivante :
1. Le **content script** (JavaScript) extrait les donnees DOM de la page
2. Le **Service Worker** envoie ces donnees au **moteur WASM** (Rust compile)
3. Le moteur WASM calcule les scores et retourne le rapport JSON
4. Le **renderer** (JavaScript) affiche les resultats dans le popup ou le panneau lateral

---

### 15. Comment mettre a jour l'extension ?

### Depuis un ZIP

1. Telecharger la nouvelle version depuis les releases GitHub
2. Extraire le ZIP
3. Remplacer le contenu du dossier `extension/` existant par les nouveaux fichiers
4. Ouvrir `chrome://extensions/`
5. Cliquer sur l'icone de rechargement (fleche circulaire) de l'extension Deltopide
6. Verifier la nouvelle version dans le popup

### Depuis les sources

```bash
cd web-audit-tool
git pull origin main

# Si le moteur Rust a change
cd audit-engine-rs
wasm-pack build --target web --release
cp pkg/audit_engine_bg.wasm ../extension/
cp pkg/audit_engine.js ../extension/
```

Puis recharger dans `chrome://extensions/`.

### Notes importantes

- La **licence est conservee** lors de la mise a jour (stockee dans `chrome.storage.local`)
- Les **resultats d'audit precedents** ne sont pas conserves — exporter en JSON avant de mettre a jour si necessaire
- Verifier la version dans le pied de page du popup apres la mise a jour

---

*Deltopide Web Audit — Eddie Plot, Deltopide SL — 2026*
