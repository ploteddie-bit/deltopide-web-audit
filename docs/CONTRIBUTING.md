# Guide de contribution — Deltopide Web Audit

> Merci de vouloir contribuer. Ce document decrit le workflow, les conventions et les procedures a suivre.

---

## Table des matieres

1. [Workflow Fork + Branch + PR](#workflow-fork--branch--pr)
2. [Ajouter un nouveau check](#ajouter-un-nouveau-check)
3. [Conventions de code](#conventions-de-code)
4. [Modifier le moteur Rust/WASM](#modifier-le-moteur-rustwasm)
5. [Tests manuels](#tests-manuels)
6. [Rapport de bugs](#rapport-de-bugs)

---

## Workflow Fork + Branch + PR

### 1. Forker le depot

```bash
# Sur GitHub, cliquer "Fork" sur ploteddie-bit/web-audit-tool
# Puis cloner votre fork
git clone git@github.com:VOTRE-USER/web-audit-tool.git
cd web-audit-tool
```

### 2. Ajouter le remote upstream

```bash
git remote add upstream git@github.com:ploteddie-bit/web-audit-tool.git
git fetch upstream
```

### 3. Creer une branche de travail

Nommer la branche selon le type de modification :

| Prefixe | Usage | Exemple |
|---------|-------|---------|
| `feat/` | Nouveau check ou fonctionnalite | `feat/check-aria-roles` |
| `fix/` | Correction de bug | `fix/score-calculation` |
| `docs/` | Documentation | `docs/faq-update` |
| `refactor/` | Refactoring sans changement fonctionnel | `refactor/renderer-split` |

```bash
git checkout -b feat/check-aria-roles upstream/main
```

### 4. Developper et committer

```bash
# Commits atomiques avec messages clairs
git add extension/content.js
git commit -m "feat: ajouter detection des roles ARIA dans content.js"
```

### 5. Pousser et creer la Pull Request

```bash
git push origin feat/check-aria-roles
```

Sur GitHub, creer une PR vers `ploteddie-bit/web-audit-tool:main` avec :
- Un titre court et descriptif
- Une description des changements
- Les checks ajoutes/modifies
- Des captures d'ecran si l'UI est modifiee

### 6. Review et merge

- Le mainteneur (Eddie) review la PR
- Corriger les retours demandes
- Le merge est fait par le mainteneur uniquement

---

## Ajouter un nouveau check

### Architecture d'un check

Chaque check suit un schema identique. Voici la structure a respecter.

### Etape 1 — Collecter les donnees dans `content.js`

Si le check necessite de nouvelles donnees DOM, les extraire dans la fonction `analyzePage()` de `content.js` :

```javascript
// Dans analyzePage() — content.js
const monNouveauChamp = doc.querySelectorAll('[role="banner"]').length;

// Ajouter au return
return {
    // ... champs existants ...
    mon_nouveau_champ: monNouveauChamp,
};
```

Regles :
- Toujours limiter les resultats (`.slice(0, N)`) pour eviter les messages oversized
- Tronquer les textes longs (`.substring(0, 200)`)
- Ne jamais envoyer de HTML brut — extraire uniquement les valeurs utiles

### Etape 2 — Ajouter le check dans le moteur Rust (`lib.rs`)

Ajouter le champ dans la structure `DomData` :

```rust
pub struct DomData {
    // ... champs existants ...
    pub mon_nouveau_champ: usize,
}
```

Creer la fonction de check dans `lib.rs` :

```rust
fn check_mon_nouveau_test(dom: &DomData) -> CheckResult {
    let (status, detail) = if dom.mon_nouveau_champ >= 2 {
        ("OK", format!("{} elements detectes", dom.mon_nouveau_champ))
    } else if dom.mon_nouveau_champ == 1 {
        ("A_CORRIGER", "1 seul element detecte, 2 recommandes".into())
    } else {
        ("ABSENT", "Aucun element detecte".into())
    };

    CheckResult {
        name: "Mon Nouveau Test".into(),
        category: "TECH".into(),  // Pilier : TECH, SEO, GEO ou SXG
        status: status.into(),
        detail,
    }
}
```

Ajouter l'appel dans la fonction `run_audit()` :

```rust
checks.push(check_mon_nouveau_test(&dom));
```

### Etape 3 — Compiler et tester

```bash
cd audit-engine-rs
wasm-pack build --target web --release
cp pkg/audit_engine_bg.wasm ../extension/
cp pkg/audit_engine.js ../extension/
```

Recharger l'extension dans Chrome et tester sur plusieurs sites.

### Piliers disponibles

| Code | Pilier | Vocation |
|------|--------|----------|
| `TECH` | Fondations Techniques | HTML, meta, performance, accessibilite |
| `SEO` | Contenu & Autorite SEO | Contenu, liens, E-E-A-T, signaux de confiance |
| `GEO` | Visibilite IA | Crawlers IA, structure LLM-friendly, llms.txt |
| `SXG` | SXG / CBOR-Web | CBOR, Signed Exchanges, headers securite, CDN |

### Donnees DOM disponibles

Avant d'ajouter un champ dans `content.js`, verifier s'il existe deja dans la structure `DomData` de `lib.rs`. Les donnees deja collectees incluent :

- Meta tags : `title`, `meta_desc`, `canonical`, `viewport`, `lang`, `charset`
- Open Graph : `og` (HashMap)
- Headings : `h1`, `h2`, `h3` (vecteurs)
- Texte : `word_count`, `html_size`, `is_spa`
- Schemas : `schemas` (vecteur de `SchemaItem`)
- Images : `images_total`, `images_without_alt`
- Liens : `internal_links_count`, `external_links_count`, `social_links`
- Structure : `tables`, `lists`, `definition_lists`, `blockquotes`
- GEO : `stats_found`, `faq_patterns`, `has_llms_txt_link`
- E-E-A-T : `has_about_page`, `has_contact_page`, `has_privacy_page`, `has_author_info`, `has_testimonials`
- Core Web Vitals : `cwv` (TTFB, FCP, LCP, CLS)
- Accessibilite : `has_skip_link`, `aria_landmarks`

---

## Conventions de code

### JavaScript (Extension Chrome)

| Regle | Detail |
|-------|--------|
| Standard | ES2020 (modules, async/await, optional chaining) |
| Style | Vanilla JS — pas de framework, pas de jQuery |
| XSS | **Toute insertion HTML** doit passer par `escapeHtml()` (defini dans `renderer.js`). Aucune exception |
| Seuils | Commenter chaque seuil avec sa justification : `// Seuil 300 mots = minimum SEO recommande` |
| Variables | `camelCase` pour les variables, `UPPER_SNAKE` pour les constantes |
| Strings | Guillemets doubles pour le HTML, backticks pour les template literals |
| Console | `console.log("[Deltopide]", ...)` — toujours prefixer avec `[Deltopide]` |

### Rust (Moteur WASM)

| Regle | Detail |
|-------|--------|
| Edition | Rust 2021 |
| Naming | `snake_case` pour les fonctions et champs, `CamelCase` pour les structs |
| Serde | Utiliser `#[serde(default)]` sur toutes les structs deserializees |
| Erreurs | Ne jamais `unwrap()` en production — utiliser `unwrap_or_default()` ou gerer le `Result` |
| Commentaires | Documenter chaque check : nom, pilier, seuils, source du seuil |

### Conventions generales

- Pas de dependances externes dans l'extension (tout est standalone)
- Pas de requetes vers des serveurs tiers (tout se fait localement)
- Pas de tracking, pas de telemetrie, pas de cookies
- Chaque fichier commence par un bloc d'en-tete avec le nom et le copyright

---

## Modifier le moteur Rust/WASM

### Prerequis

```bash
# Installer Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Ajouter la target WASM
rustup target add wasm32-unknown-unknown

# Installer wasm-pack
cargo install wasm-pack
```

### Cycle de modification

```bash
# 1. Editer le code Rust
cd audit-engine-rs
# Modifier src/lib.rs

# 2. Compiler en WASM
wasm-pack build --target web --release

# 3. Copier les artefacts dans l'extension
cp pkg/audit_engine_bg.wasm ../extension/
cp pkg/audit_engine.js ../extension/

# 4. Recharger l'extension dans Chrome
#    chrome://extensions/ → icone de rechargement

# 5. Tester sur un site
```

### Structure du moteur

```
audit-engine-rs/
    Cargo.toml          # Dependances : wasm-bindgen, serde, serde_json, js-sys, web-sys
    src/
        lib.rs          # Point d'entree unique — structs, checks, run_audit(), validate_license()
```

### Fonctions WASM exposees

| Fonction | Signature | Role |
|----------|-----------|------|
| `run_audit` | `(dom_json: &str, server_json: &str) -> String` | Execute tous les checks et retourne le rapport JSON |
| `validate_license` | `(key: &str) -> bool` | Valide une cle de licence |
| `get_version` | `() -> String` | Retourne la version du moteur |

### Profil de compilation

Le `Cargo.toml` est configure pour minimiser la taille du binaire WASM :

```toml
[profile.release]
opt-level = "z"     # Optimiser pour la taille
lto = true          # Link-Time Optimization
strip = true        # Supprimer les symboles de debug
codegen-units = 1   # Compilation mono-thread pour meilleure optimisation
```

Ne pas modifier ces parametres sans raison documentee.

---

## Tests manuels

Avant de soumettre une PR, tester l'extension sur **3 types de sites minimum** :

### 1. Site statique classique

- Exemple : un blog WordPress, un site vitrine HTML/CSS
- Verifier que tous les checks retournent un resultat coherent
- Le score Fondations Techniques doit etre calculable

### 2. Single Page Application (SPA)

- Exemple : une application React, Vue.js ou Angular
- Verifier la detection SPA (`is_spa`)
- Verifier que le content script attend le chargement du DOM
- Le volume de texte et les headings doivent etre detectes malgre le rendu client-side

### 3. Site multilingue / international

- Exemple : un site avec `hreflang`, plusieurs langues
- Verifier la detection des hreflangs
- Verifier que l'attribut `lang` est correctement lu
- Verifier la detection du canonical sur le bon domaine

### Checklist de test

Pour chaque site teste :

- [ ] L'audit se lance sans erreur
- [ ] Le score global est affiche
- [ ] Les 4 piliers ont un score
- [ ] Le Top 8 des actions prioritaires est pertinent
- [ ] L'export JSON est valide (ouvrir dans un editeur JSON)
- [ ] L'export CSV est lisible
- [ ] Le panneau lateral affiche tous les checks
- [ ] Pas d'erreur dans la console du Service Worker (`chrome://extensions/` → Inspecter)

---

## Rapport de bugs

Pour signaler un bug, ouvrir une issue sur GitHub avec les informations suivantes :

### Informations obligatoires

| Champ | Detail |
|-------|--------|
| **Version de l'extension** | Visible dans le footer du popup (ex: v1.2.0) |
| **Version de Chrome** | `chrome://settings/help` (ex: 126.0.6478.126) |
| **URL du site concerne** | L'URL exacte ou le probleme survient |
| **Comportement attendu** | Ce qui devrait se passer |
| **Comportement observe** | Ce qui se passe reellement |

### Informations recommandees

- **Capture d'ecran** de l'extension montrant le probleme
- **Logs de la console** du Service Worker : `chrome://extensions/` → "Inspecter les vues : Service Worker" → onglet Console
- **Logs de la console** de la page : F12 → Console (filtrer par `[Deltopide]`)
- **Systeme d'exploitation** : Windows / macOS / Linux + version

### Exemple de rapport

```
## Bug : score GEO affiche 0% alors que llms.txt existe

**Version** : v1.2.0
**Chrome** : 126.0.6478.126
**URL** : https://example.com
**OS** : macOS 14.5

### Comportement attendu
Le check "llms.txt" devrait etre OK car le fichier existe a https://example.com/llms.txt

### Comportement observe
Le check affiche ABSENT. Le score GEO est 0%.

### Console Service Worker
[Deltopide] Fetch llms.txt: status 403

### Capture d'ecran
(joindre la capture)
```

---

*Deltopide Web Audit — Eddie Plot, Deltopide SL — 2026*
