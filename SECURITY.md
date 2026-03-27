# Securite

## Modele de menace

L'extension Chrome Deltopide Web Audit analyse le DOM de pages web visitees par l'utilisateur. Les menaces principales sont :

| Menace | Protection |
|--------|-----------|
| XSS via donnees DOM | Toutes les insertions HTML passent par `escapeHtml()` |
| Injection de code | CSP `script-src 'self'` interdit tout script externe |
| Piratage / copie | Licence obligatoire + code obfusque |
| Modification des fichiers | Integrite SHA-256 verifiee a chaque audit |
| Extraction automatisee | Rate limiting 30 req/min |
| Donnees oversized | Limites sur headings (20), images (100), schemas (20), texte (2000 chars) |

## Systeme de licence

L'extension necessite une cle de licence valide pour fonctionner.

- Format : `DELTOPIDE-XXXX-XXXX-XXXX`
- Validation : SHA-256 HMAC avec salt interne
- Stockage : `chrome.storage.local` (local a la machine)
- Expiration : date codee dans le build (renouvellement annuel)

Sans cle valide, l'extension affiche un ecran d'activation et refuse tout audit.

## Integrite des fichiers

A l'installation, le service worker calcule le SHA-256 de chaque fichier JS et le stocke. A chaque audit, les hashes sont recalcules et compares. Si un fichier a ete modifie, l'extension affiche une erreur et refuse de fonctionner.

## Content Security Policy

```json
{
  "extension_pages": "script-src 'self'; object-src 'none'; style-src 'self' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com;"
}
```

## Permissions

| Permission | Usage |
|-----------|-------|
| `activeTab` | Acces a l'onglet actif uniquement |
| `scripting` | Injection du content script a la demande |
| `sidePanel` | Panneau lateral Chrome |
| `storage` | Cache des resultats + licence |
| `<all_urls>` | Fetch robots.txt, sitemap.xml, index.cbor sur le domaine audite |

## Signaler une vulnerabilite

Contactez security@deltopide.com avec :
- Description de la vulnerabilite
- Etapes pour reproduire
- Impact potentiel

Nous repondons sous 48h.
