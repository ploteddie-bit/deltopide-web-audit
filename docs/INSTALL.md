# Guide d'installation — Deltopide Web Audit

> Extension Chrome d'audit web SEO / GEO / CBOR-Web avec moteur Rust/WASM.
> Standard Deltopide v1.2 — 35 checks sur 4 piliers.

---

## Table des matieres

1. [Prerequis](#prerequis)
2. [Installation depuis un ZIP (recommande)](#installation-depuis-un-zip)
3. [Installation depuis les sources](#installation-depuis-les-sources)
4. [Activation de la licence](#activation-de-la-licence)
5. [Mise a jour](#mise-a-jour)
6. [Desinstallation](#desinstallation)
7. [Installation CLI Python](#installation-cli-python)
8. [Depannage](#depannage)

---

## Prerequis

| Element | Requis |
|---------|--------|
| Navigateur | Google Chrome **114** ou superieur (Manifest V3 requis) |
| Systeme | Windows, macOS ou Linux |
| Cle de licence | Format `DELTOPIDE-XXXX-XXXX-XXXX` (fournie a l'achat ou sur demande) |
| Espace disque | ~5 Mo (extension + moteur WASM) |

> **Note** : Les navigateurs bases sur Chromium (Brave, Edge, Opera) fonctionnent en general, mais seul Chrome est officiellement supporte.

---

## Installation depuis un ZIP

### Etape 1 — Telecharger l'archive

Telecharger la derniere release depuis le depot GitHub prive :

```
https://github.com/ploteddie-bit/web-audit-tool/releases
```

Le fichier se nomme `deltopide-web-audit-vX.Y.Z.zip`.

<!-- Screenshot: page de release GitHub avec le lien de telechargement -->

### Etape 2 — Dezipper l'archive

Extraire le contenu du ZIP dans un dossier permanent (par exemple `~/deltopide-audit/` ou `C:\deltopide-audit\`).

> **Important** : ne pas placer le dossier dans un repertoire temporaire ou sur un disque amovible. Chrome a besoin d'un acces permanent aux fichiers de l'extension.

<!-- Screenshot: contenu du dossier apres extraction (manifest.json, background.js, etc.) -->

### Etape 3 — Ouvrir la page des extensions Chrome

Dans la barre d'adresse de Chrome, taper :

```
chrome://extensions/
```

Puis activer le **Mode developpeur** via le toggle en haut a droite de la page.

<!-- Screenshot: page chrome://extensions avec le toggle Mode developpeur entoure -->

### Etape 4 — Charger l'extension

Cliquer sur le bouton **Charger l'extension non empaquetee** (en haut a gauche).

Naviguer jusqu'au dossier `extension/` extrait a l'etape 2 et le selectionner.

<!-- Screenshot: boite de dialogue de selection du dossier extension/ -->

### Etape 5 — Verifier l'installation

L'extension **Deltopide Web Audit** apparait dans la liste avec son icone. Verifier que :
- Le toggle est active (bleu)
- Aucune erreur n'est affichee
- L'icone Deltopide apparait dans la barre d'outils Chrome

<!-- Screenshot: extension visible dans chrome://extensions avec statut actif -->

Epingler l'extension dans la barre Chrome en cliquant sur l'icone puzzle, puis sur l'epingle a cote de "Deltopide Audit".

---

## Installation depuis les sources

Pour les developpeurs souhaitant compiler le moteur Rust/WASM eux-memes.

### Prerequis supplementaires

| Element | Version |
|---------|---------|
| Rust | Edition 2021 (rustup recommande) |
| wasm-pack | 0.12+ |
| Target WASM | `wasm32-unknown-unknown` |

### Etapes

```bash
# 1. Cloner le depot
git clone git@github.com:ploteddie-bit/web-audit-tool.git
cd web-audit-tool

# 2. Installer la target WASM (si pas deja fait)
rustup target add wasm32-unknown-unknown

# 3. Installer wasm-pack (si pas deja fait)
cargo install wasm-pack

# 4. Compiler le moteur Rust en WASM
cd audit-engine-rs
wasm-pack build --target web --release

# 5. Copier les fichiers generes dans l'extension
cp pkg/audit_engine_bg.wasm ../extension/
cp pkg/audit_engine.js ../extension/

# 6. Charger l'extension dans Chrome
#    Suivre les etapes 3 a 5 de la section precedente
#    en selectionnant le dossier extension/
```

> **Note** : le profil de compilation est optimise (`opt-level = "z"`, LTO, strip) pour minimiser la taille du binaire WASM.

---

## Activation de la licence

Au premier lancement de l'extension, un ecran d'activation s'affiche.

1. Entrer la cle de licence au format :

```
DELTOPIDE-XXXX-XXXX-XXXX
```

2. Cliquer sur **Activer**
3. L'extension valide la cle via le moteur WASM (verification SHA-256 HMAC locale)
4. En cas de succes, l'interface d'audit apparait

### Informations importantes

- La cle est stockee localement dans `chrome.storage.local` (jamais transmise a un serveur)
- La licence expire au bout d'un an (date codee dans le build)
- Une seule cle peut etre active par profil Chrome
- En cas de changement de machine, reutiliser la meme cle

### Obtenir une cle

Contactez **contact@deltopide.com** ou rendez-vous sur [deltopide.fr](https://deltopide.fr) pour obtenir une cle de licence.

---

## Mise a jour

### Extension Chrome

1. Telecharger la nouvelle version (ZIP ou `git pull`)
2. Remplacer le contenu du dossier `extension/` par les nouveaux fichiers
3. Ouvrir `chrome://extensions/`
4. Cliquer sur l'icone de rechargement (fleche circulaire) sur la carte de l'extension
5. Verifier la version dans le popup (coin inferieur)

> La licence et les parametres sont conserves lors de la mise a jour car ils sont stockes dans `chrome.storage.local`, independamment des fichiers de l'extension.

### CLI Python

```bash
cd web-audit-tool
git pull origin main
```

Aucune reinstallation necessaire — le script `audit.py` est standalone.

---

## Desinstallation

### Extension Chrome

1. Ouvrir `chrome://extensions/`
2. Trouver **Deltopide Web Audit**
3. Cliquer sur **Supprimer**
4. Confirmer la suppression
5. (Optionnel) Supprimer le dossier local de l'extension

### CLI Python

Supprimer le fichier `audit.py` et desinstaller les dependances si elles ne sont plus utiles :

```bash
pip uninstall requests beautifulsoup4 lxml
```

---

## Installation CLI Python

Le CLI Python est un outil standalone qui ne necessite pas l'extension Chrome.

### Installation

```bash
# Installer les dependances
pip install requests beautifulsoup4 lxml

# Verifier l'installation
python3 audit.py --help
```

### Utilisation rapide

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

### Dependances

| Paquet | Role |
|--------|------|
| `requests` | Requetes HTTP vers les sites audites |
| `beautifulsoup4` | Parsing HTML / extraction DOM |
| `lxml` | Parser HTML performant (backend BeautifulSoup) |

---

## Depannage

### L'extension ne se charge pas dans Chrome

- Verifier que le **Mode developpeur** est active dans `chrome://extensions/`
- Verifier que le dossier selectionne contient bien `manifest.json` a la racine
- Verifier la version de Chrome (114 minimum requis pour Manifest V3 complet)
- Si le message "Manifest version 2 is deprecated" apparait, vous avez une ancienne version de l'extension

### Erreur "Extension corrompue" ou "Integrite compromise"

L'extension verifie l'integrite SHA-256 de ses fichiers JS a chaque audit. Cette erreur signifie qu'un fichier a ete modifie apres installation.

- Retelecharger l'archive originale et reinstaller
- Ne pas modifier manuellement les fichiers JS de l'extension
- Si vous compilez depuis les sources, recopier `audit_engine_bg.wasm` et `audit_engine.js` depuis `pkg/`

### Licence invalide

- Verifier le format exact : `DELTOPIDE-XXXX-XXXX-XXXX` (4 groupes, tirets inclus)
- Verifier que la cle n'a pas expire (validite 1 an)
- Pas d'espaces avant/apres la cle
- En cas de doute, contacter contact@deltopide.com

### L'audit echoue sur certains sites

Certains sites peuvent bloquer les requetes de l'extension :

- **Sites avec CSP strict** : le content script peut ne pas s'injecter correctement. Recharger la page et relancer l'audit
- **Sites necessitant une authentification** : se connecter d'abord, puis lancer l'audit
- **Pages vides ou SPA** : attendre que le contenu soit charge avant de lancer l'audit
- **Erreur reseau** : verifier la connexion internet (l'extension fait des requetes fetch vers robots.txt, sitemap.xml, etc.)
- **Pages chrome://, about:, extensions** : l'extension ne peut pas auditer les pages internes du navigateur

### Erreur WASM (moteur non charge)

Si l'audit affiche "Moteur WASM non charge" :

- Fermer completement Chrome et le relancer
- Verifier que le fichier `audit_engine_bg.wasm` est present dans le dossier de l'extension
- Verifier que le fichier n'est pas corrompu (le retelecharger si necessaire)
- Dans `chrome://extensions/`, cliquer sur "Inspecter les vues : Service Worker" et verifier la console pour les erreurs detaillees
- Si la CSP du navigateur bloque WASM, verifier qu'aucune extension de securite ne modifie les headers

---

*Deltopide Web Audit — Eddie Plot, Deltopide SL — 2026*
