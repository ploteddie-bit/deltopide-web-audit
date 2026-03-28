# Privacy Policy — Deltopide Web Audit

**Last updated:** 2026-03-28

## Overview

Deltopide Web Audit is a Chrome browser extension developed by Deltopide SL. This extension performs web page audits within your browser using a Rust/WebAssembly engine. We are committed to protecting your privacy and being transparent about data usage.

## Data collection

### License validation

When you activate your license key, the extension contacts our license server (`deltopide-audit-license.explodev.workers.dev`) to validate your key. The following data is transmitted:

- Your license key
- A device identifier (generated locally, used to prevent key sharing)
- Your IP address (logged automatically by the server)

### Audit logging

Each time you run an audit, the following data is sent to our server:

- The URL of the audited page
- Your license key
- Your device identifier
- Your IP address
- Timestamp

This data is used for:
- License management (audit count per user)
- Product improvement (understanding usage patterns)
- Abuse prevention

### What we do NOT collect

- We do **not** collect the content of audited pages
- We do **not** track your browsing activity beyond audited pages
- We do **not** use third-party analytics or telemetry
- We do **not** set or read cookies
- We do **not** collect geolocation data
- We do **not** display advertisements
- We do **not** sell, share, or monetize any user data

## Permissions used

| Permission | Purpose |
|---|---|
| `activeTab` | Access the current tab's page content to perform the audit |
| `sidePanel` | Display audit results in Chrome's side panel |
| `scripting` | Inject the content analysis script into the audited page |
| `storage` | Save license key, audit cache, and preferences locally |
| `<all_urls>` (host) | Allow auditing any website — only activates when triggered by the user |

## Local storage

Audit results and scores are stored locally on your device using `chrome.storage`. This data never leaves your browser. You can clear it by removing the extension.

## Data hosting

All server-side data is hosted on Cloudflare Workers (edge network, EU region). No data is stored on US-only servers. Deltopide SL is subject to European data protection regulations (RGPD).

## Data retention

- License validation logs: retained for the duration of the license
- Audit logs: retained for 12 months, then automatically deleted
- Feedback messages: retained until resolved

## Your rights (RGPD)

You have the right to:
- Access your personal data
- Request correction or deletion of your data
- Export your data
- Withdraw consent

Contact us at contact@deltopide.com to exercise these rights.

## Changes to this policy

If we update this privacy policy, we will publish the revised version with an updated date. Significant changes will be communicated through the Chrome Web Store listing.

## Contact

- **Email:** contact@deltopide.com
- **Website:** https://deltopide.fr
- **Publisher:** Deltopide SL — CIF B24976516
