#!/usr/bin/env python3
"""
DELTOPIDE WEB AUDIT TOOL v1.0
==============================
Audit automatise SEO / GEO / SXG-CBOR pour n'importe quel site web.

Usage:
    python3 audit.py https://www.example.com
    python3 audit.py https://www.example.com --output rapport.json
    python3 audit.py https://www.example.com --format html --output rapport.html

Dependances:
    pip install requests beautifulsoup4 lxml

Auteur: Standard Deltopide — Mars 2026
"""

import sys
import json
import time
import re
import argparse
from datetime import datetime
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

# ============================================================
# CONFIGURATION
# ============================================================

TIMEOUT = 15
USER_AGENT = "Mozilla/5.0 (compatible; DeltopideAudit/1.0)"
HEADERS = {"User-Agent": USER_AGENT}

AI_BOTS = {
    "GPTBot": "ChatGPT (OpenAI)",
    "ChatGPT-User": "ChatGPT Navigation",
    "Google-Extended": "Gemini (Google)",
    "ClaudeBot": "Claude (Anthropic)",
    "PerplexityBot": "Perplexity",
    "Bytespider": "TikTok/ByteDance",
    "Googlebot": "Google Search",
    "Bingbot": "Bing Search",
    "Twitterbot": "Twitter/X",
    "facebookexternalhit": "Facebook",
    "LinkedInBot": "LinkedIn",
}

SCHEMA_TYPES_UTILES = [
    "Organization", "LocalBusiness", "Product", "Course", "Event",
    "FAQPage", "Article", "BlogPosting", "BreadcrumbList", "WebSite",
    "HowTo", "Person", "Service", "Offer", "Review", "AggregateRating",
    "VideoObject", "ImageObject", "NGO",
]

# ============================================================
# CLASSES DE RESULTATS
# ============================================================

class Check:
    def __init__(self, name, category, status="ABSENT", detail="", value=None):
        self.name = name
        self.category = category
        self.status = status
        self.detail = detail
        self.value = value

    def ok(self, detail="", value=None):
        self.status = "OK"
        self.detail = detail
        self.value = value
        return self

    def warn(self, detail="", value=None):
        self.status = "A_CORRIGER"
        self.detail = detail
        self.value = value
        return self

    def absent(self, detail="", value=None):
        self.status = "ABSENT"
        self.detail = detail
        self.value = value
        return self

    def to_dict(self):
        return {
            "name": self.name,
            "category": self.category,
            "status": self.status,
            "detail": self.detail,
            "value": self.value,
        }


class AuditReport:
    def __init__(self, url):
        self.url = url
        self.domain = urlparse(url).netloc
        self.timestamp = datetime.now().isoformat()
        self.checks = []
        self.raw_data = {}

    def add(self, check):
        self.checks.append(check)
        return check

    def score(self, category=None):
        filtered = [c for c in self.checks if category is None or c.category == category]
        ok = sum(1 for c in filtered if c.status == "OK")
        total = len(filtered)
        return ok, total

    def summary(self):
        categories = ["TECH", "SEO", "GEO", "SXG"]
        result = {}
        for cat in categories:
            ok, total = self.score(cat)
            result[cat] = {"ok": ok, "total": total, "pct": round(ok/total*100) if total else 0}
        ok_all, total_all = self.score()
        result["TOTAL"] = {"ok": ok_all, "total": total_all, "pct": round(ok_all/total_all*100) if total_all else 0}
        return result

    def priorities(self):
        actions = []
        for c in self.checks:
            if c.status != "OK":
                impact = 3 if c.category == "TECH" else 2 if c.category == "SEO" else 1
                if "sitemap" in c.name.lower() or "ssr" in c.name.lower() or "robots" in c.name.lower():
                    impact += 2
                if "schema" in c.name.lower() or "blog" in c.name.lower():
                    impact += 1
                actions.append((impact, c))
        actions.sort(key=lambda x: -x[0])
        return actions[:10]

    def to_dict(self):
        return {
            "url": self.url,
            "domain": self.domain,
            "timestamp": self.timestamp,
            "summary": self.summary(),
            "checks": [c.to_dict() for c in self.checks],
            "priorities": [{"impact": i, **c.to_dict()} for i, c in self.priorities()],
            "raw_data": self.raw_data,
        }


# ============================================================
# FONCTIONS UTILITAIRES
# ============================================================

def fetch(url, allow_redirects=True, timeout=TIMEOUT):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=allow_redirects)
        return r
    except Exception:
        return None

def fetch_head(url, timeout=TIMEOUT):
    try:
        r = requests.head(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        return r
    except Exception:
        return None

def safe_text(soup_element):
    if soup_element:
        return soup_element.get_text(strip=True) if hasattr(soup_element, 'get_text') else str(soup_element)
    return ""

def print_status(icon, text):
    print(f"  {icon} {text}")

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


# ============================================================
# PILIER 1 : FONDATIONS TECHNIQUES
# ============================================================

def audit_ssr(report, url, html_content, html_size):
    check = report.add(Check("Rendu serveur (SSR)", "TECH"))
    report.raw_data["html_size_bytes"] = html_size
    has_root_div = bool(re.search(r'<div\s+id=["\']root["\']\s*>\s*</div>', html_content))
    has_app_div = bool(re.search(r'<div\s+id=["\']app["\']\s*>\s*</div>', html_content))
    is_spa = (has_root_div or has_app_div) and html_size < 10000
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(['script', 'style', 'meta', 'link', 'noscript']):
        tag.decompose()
    visible_text = soup.get_text(strip=True)
    text_length = len(visible_text)
    if is_spa and text_length < 500:
        check.absent(f"SPA detectee (HTML: {html_size} octets, texte visible: {text_length} car.). Contenu invisible pour Google.", {"html_size": html_size, "visible_text_length": text_length, "is_spa": True})
    elif html_size < 5000:
        check.warn(f"HTML leger ({html_size} octets, texte: {text_length} car.).", {"html_size": html_size, "visible_text_length": text_length})
    else:
        check.ok(f"HTML riche ({html_size} octets, texte visible: {text_length} car.).", {"html_size": html_size, "visible_text_length": text_length, "is_spa": False})
    status_icon = {"OK": "✅", "A_CORRIGER": "⚠️", "ABSENT": "❌"}[check.status]
    print_status(status_icon, f"SSR: {check.detail[:80]}...")
    return check

def audit_sitemap(report, url):
    check = report.add(Check("Sitemap XML", "TECH"))
    base = urlparse(url)
    sitemap_url = f"{base.scheme}://{base.netloc}/sitemap.xml"
    r = fetch(sitemap_url)
    if not r or r.status_code != 200:
        check.absent(f"Sitemap non trouve a {sitemap_url}")
        print_status("❌", f"Sitemap: absent")
        return check
    content = r.text
    if '<urlset' not in content and '<sitemapindex' not in content:
        check.absent("Le fichier sitemap.xml ne contient pas de XML valide")
        print_status("❌", "Sitemap: pas de XML valide")
        return check
    urls_found = re.findall(r'<loc>(.*?)</loc>', content)
    url_count = len(urls_found)
    sub_sitemaps = re.findall(r'<loc>(.*?sitemap.*?\.xml.*?)</loc>', content)
    if sub_sitemaps:
        total_sub_urls = 0
        for sub_url in sub_sitemaps[:10]:
            sub_r = fetch(sub_url)
            if sub_r and sub_r.status_code == 200:
                sub_urls = re.findall(r'<loc>(.*?)</loc>', sub_r.text)
                total_sub_urls += len(sub_urls)
        url_count = total_sub_urls if total_sub_urls > 0 else url_count
    wrong_domain_urls = []
    domain = base.netloc
    for u in urls_found:
        parsed = urlparse(u)
        if parsed.netloc and parsed.netloc != domain and 'sitemap' not in u:
            wrong_domain_urls.append(u)
    report.raw_data["sitemap_url_count"] = url_count
    if wrong_domain_urls:
        check.warn(f"Sitemap present ({url_count} URLs) mais {len(wrong_domain_urls)} URLs mauvais domaine", {"url_count": url_count})
        print_status("⚠️", f"Sitemap: {url_count} URLs, {len(wrong_domain_urls)} mauvais domaine")
    elif url_count < 10:
        check.warn(f"Sitemap present mais seulement {url_count} URLs.", {"url_count": url_count})
        print_status("⚠️", f"Sitemap: {url_count} URLs")
    else:
        check.ok(f"Sitemap OK avec {url_count} URLs.", {"url_count": url_count})
        print_status("✅", f"Sitemap: {url_count} URLs")
    return check

def audit_robots(report, url):
    check = report.add(Check("Robots.txt", "TECH"))
    check_ai = report.add(Check("Crawlers IA autorises", "GEO"))
    base = urlparse(url)
    robots_url = f"{base.scheme}://{base.netloc}/robots.txt"
    r = fetch(robots_url)
    if not r or r.status_code != 200 or '<html' in r.text.lower()[:200]:
        check.absent(f"Robots.txt absent")
        check_ai.absent("Pas de robots.txt")
        print_status("❌", "Robots.txt: absent")
        return check
    content = r.text.lower()
    report.raw_data["robots_txt"] = r.text[:2000]
    bots_status = {}
    for bot_name, bot_desc in AI_BOTS.items():
        bot_lower = bot_name.lower()
        blocked = False
        allowed = False
        sections = re.split(r'user-agent\s*:', content)
        for section in sections:
            lines = section.strip().split('\n')
            if lines and bot_lower in lines[0].lower():
                for line in lines[1:]:
                    line = line.strip()
                    if line.startswith('disallow: /') and line.strip() == 'disallow: /':
                        blocked = True
                    elif line.startswith('allow: /'):
                        allowed = True
                    elif line.startswith('user-agent:'):
                        break
        bots_status[bot_name] = {"desc": bot_desc, "blocked": blocked, "allowed": allowed}
    blocked_bots = [b for b, s in bots_status.items() if s["blocked"]]
    ai_bots_blocked = [b for b in blocked_bots if b in ["GPTBot", "ChatGPT-User", "ClaudeBot", "PerplexityBot", "Google-Extended"]]
    report.raw_data["bots_status"] = bots_status
    check.ok(f"Robots.txt present", {"blocked_bots": blocked_bots})
    print_status("✅", "Robots.txt: present")
    if ai_bots_blocked:
        check_ai.warn(f"{len(ai_bots_blocked)} crawlers IA bloques: {', '.join(ai_bots_blocked)}", {"blocked": ai_bots_blocked})
        print_status("⚠️", f"Crawlers IA: {len(ai_bots_blocked)} bloques")
    else:
        check_ai.ok("Tous les crawlers IA autorises")
        print_status("✅", "Crawlers IA: tous autorises")
    return check

def audit_meta_tags(report, soup, html_content):
    check = report.add(Check("Meta tags SEO", "TECH"))
    issues = []
    details = {}
    title_tag = soup.find('title')
    title = safe_text(title_tag) if title_tag else ""
    details["title"] = title
    details["title_length"] = len(title)
    if not title:
        issues.append("Title absente")
    elif len(title) > 70:
        issues.append(f"Title trop long ({len(title)} car.)")
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    desc = desc_tag.get('content', '') if desc_tag else ""
    details["description_length"] = len(desc)
    if not desc:
        issues.append("Meta description absente")
    elif len(desc) > 170:
        issues.append(f"Description trop longue ({len(desc)} car.)")
    canonical = soup.find('link', attrs={'rel': 'canonical'})
    details["canonical"] = canonical.get('href', '') if canonical else "absent"
    if not canonical:
        issues.append("Canonical absent")
    html_tag = soup.find('html')
    lang = html_tag.get('lang', '') if html_tag else ""
    details["lang"] = lang
    report.raw_data["meta_tags"] = details
    if not issues:
        check.ok(f"Title: {len(title)}c | Desc: {len(desc)}c | Lang: {lang}", details)
        print_status("✅", f"Meta tags: OK")
    else:
        check.warn("; ".join(issues), details)
        print_status("⚠️", f"Meta tags: {issues[0]}")
    return check

def audit_open_graph(report, soup):
    check = report.add(Check("Open Graph + Twitter Cards", "TECH"))
    details = {}
    missing = []
    for field in ['og:title', 'og:description', 'og:image', 'og:type', 'og:url']:
        tag = soup.find('meta', attrs={'property': field})
        value = tag.get('content', '') if tag else ""
        details[field] = value
        if not value:
            missing.append(field)
    for field in ['twitter:card', 'twitter:title', 'twitter:description', 'twitter:image']:
        tag = soup.find('meta', attrs={'name': field})
        value = tag.get('content', '') if tag else ""
        details[field] = value
        if not value:
            missing.append(field)
    report.raw_data["open_graph"] = details
    if not missing:
        check.ok(f"OG et Twitter complets", details)
        print_status("✅", "OG + Twitter: complets")
    elif len(missing) <= 3:
        check.warn(f"{len(missing)} manquantes: {', '.join(missing)}", details)
        print_status("⚠️", f"OG/Twitter: {len(missing)} manquantes")
    else:
        check.absent(f"{len(missing)} manquantes: {', '.join(missing)}", details)
        print_status("❌", f"OG/Twitter: {len(missing)} manquantes")
    return check

def audit_schema(report, soup, html_content):
    check = report.add(Check("Schema.org (JSON-LD)", "TECH"))
    check_geo = report.add(Check("Schema.org pour GEO", "GEO"))
    schemas_found = []
    ld_scripts = soup.find_all('script', attrs={'type': 'application/ld+json'})
    for script in ld_scripts:
        try:
            data = json.loads(script.string)
            if isinstance(data, list):
                for item in data:
                    if '@type' in item:
                        schemas_found.append(item['@type'])
            elif isinstance(data, dict):
                if '@type' in data:
                    schemas_found.append(data['@type'])
                if '@graph' in data:
                    for item in data['@graph']:
                        if '@type' in item:
                            schemas_found.append(item['@type'])
        except (json.JSONDecodeError, TypeError):
            pass
    report.raw_data["schema_types"] = schemas_found
    if not schemas_found:
        check.absent("Aucun Schema.org detecte")
        print_status("❌", "Schema.org: absent")
    elif len(schemas_found) == 1:
        check.warn(f"1 type: {schemas_found[0]}", {"types": schemas_found})
        print_status("⚠️", f"Schema.org: {schemas_found[0]} seul")
    else:
        check.ok(f"{len(schemas_found)} types: {', '.join(schemas_found)}", {"types": schemas_found})
        print_status("✅", f"Schema.org: {', '.join(schemas_found[:4])}")
    geo_types = [t for t in schemas_found if t in ["FAQPage", "HowTo", "Article", "BlogPosting"]]
    if geo_types:
        check_geo.ok(f"Types IA: {', '.join(geo_types)}", {"types": geo_types})
        print_status("✅", f"Schema GEO: {', '.join(geo_types)}")
    elif schemas_found:
        check_geo.warn("Pas de FAQPage/HowTo/Article", {"types": schemas_found})
        print_status("⚠️", "Schema GEO: pas de types IA")
    else:
        check_geo.absent("Pas de Schema.org")
        print_status("❌", "Schema GEO: absent")
    return check

def audit_performance(report, url, response_time):
    check = report.add(Check("Performance", "TECH"))
    r = fetch_head(url)
    server = r.headers.get('server', '').lower() if r else ""
    cdn = ""
    if 'cloudflare' in server: cdn = "Cloudflare"
    elif 'shopify' in server: cdn = "Shopify"
    elif 'vercel' in server: cdn = "Vercel"
    report.raw_data["response_time"] = response_time
    report.raw_data["cdn"] = cdn
    if response_time < 2.0:
        check.ok(f"{response_time:.2f}s | CDN: {cdn or '-'}", {"time": response_time, "cdn": cdn})
        print_status("✅", f"Performance: {response_time:.2f}s")
    else:
        check.warn(f"{response_time:.2f}s (lent)", {"time": response_time})
        print_status("⚠️", f"Performance: {response_time:.2f}s")
    return check

def audit_https(report, url):
    check = report.add(Check("HTTPS", "TECH"))
    if urlparse(url).scheme == 'https':
        check.ok("HTTPS actif")
        print_status("✅", "HTTPS: actif")
    else:
        check.absent("Pas de HTTPS")
        print_status("❌", "HTTPS: absent")
    return check

def audit_mobile(report, soup):
    check = report.add(Check("Mobile / Viewport", "TECH"))
    viewport = soup.find('meta', attrs={'name': 'viewport'})
    if viewport:
        check.ok("Viewport present")
        print_status("✅", "Mobile: viewport OK")
    else:
        check.absent("Viewport absent")
        print_status("❌", "Mobile: viewport absent")
    return check

# ============================================================
# PILIER 2
# ============================================================

def audit_content_volume(report, url):
    check = report.add(Check("Volume de contenu", "SEO"))
    url_count = report.raw_data.get("sitemap_url_count", 0)
    if url_count == 0:
        check.absent("Volume inconnu (pas de sitemap)")
        print_status("❌", "Contenu: inconnu")
    elif url_count < 10:
        check.warn(f"{url_count} pages (recommande: 20+)", {"count": url_count})
        print_status("⚠️", f"Contenu: {url_count} pages")
    else:
        check.ok(f"{url_count} pages", {"count": url_count})
        print_status("✅", f"Contenu: {url_count} pages")
    return check

def audit_headings(report, soup):
    check = report.add(Check("Structure H1/H2/H3", "SEO"))
    h1s = soup.find_all('h1')
    h2s = soup.find_all('h2')
    issues = []
    if len(h1s) == 0:
        issues.append("Aucun H1")
    elif len(h1s) > 1:
        issues.append(f"{len(h1s)} H1 (recommande: 1)")
    if not issues:
        check.ok(f"H1: {len(h1s)} | H2: {len(h2s)}")
        print_status("✅", f"Titres: H1={len(h1s)}, H2={len(h2s)}")
    else:
        check.warn("; ".join(issues))
        print_status("⚠️", f"Titres: {issues[0]}")
    return check

def audit_mentions_legales(report, url, soup):
    check = report.add(Check("Mentions legales", "SEO"))
    links = soup.find_all('a', href=True)
    legal = [l for l in links if any(t in l.get('href', '').lower() for t in ['mention', 'legal', 'privacy', 'confidential'])]
    if legal:
        check.ok("Pages legales detectees")
        print_status("✅", "Mentions legales: OK")
    else:
        check.warn("Non detectees")
        print_status("⚠️", "Mentions legales: non detectees")
    return check

def audit_eeat(report, soup):
    check = report.add(Check("Signaux E-E-A-T", "SEO"))
    signals = []
    links = soup.find_all('a', href=True)
    about = [l for l in links if any(t in l.get('href', '').lower() for t in ['about', 'a-propos', 'equipe', 'notre-histoire'])]
    if about: signals.append("Page A propos")
    text = soup.get_text().lower()
    if any(t in text for t in ['temoignage', 'avis', 'review']): signals.append("Temoignages")
    if any(t in text for t in ['certifi', 'label', 'bio', 'iso']): signals.append("Certifications")
    if len(signals) >= 2:
        check.ok(f"{', '.join(signals)}")
        print_status("✅", f"E-E-A-T: {', '.join(signals)}")
    elif signals:
        check.warn(f"{signals[0]} seul")
        print_status("⚠️", f"E-E-A-T: {signals[0]}")
    else:
        check.warn("Aucun signal")
        print_status("⚠️", "E-E-A-T: aucun signal")
    return check

# ============================================================
# PILIER 3
# ============================================================

def audit_geo_content_structure(report, soup, html_content):
    check = report.add(Check("Structure contenu GEO", "GEO"))
    h2s = soup.find_all('h2')
    question_h2s = [h for h in h2s if '?' in safe_text(h)]
    if question_h2s:
        check.ok(f"{len(question_h2s)} H2 en questions")
        print_status("✅", f"GEO: {len(question_h2s)} H2 en questions")
    else:
        check.warn("Aucun H2 en question")
        print_status("⚠️", "GEO: H2 pas en questions")
    return check

def audit_geo_citable_data(report, soup):
    check = report.add(Check("Donnees citables", "GEO"))
    text = soup.get_text()
    numbers = re.findall(r'\d+\s*%', text)
    if len(numbers) > 0:
        check.ok(f"{len(numbers)} stats detectees")
        print_status("✅", f"Donnees citables: {len(numbers)} stats")
    else:
        check.warn("Peu de donnees citables")
        print_status("⚠️", "Donnees citables: peu")
    return check

# ============================================================
# PILIER 4
# ============================================================

def audit_sxg(report, url):
    check_sxg = report.add(Check("SXG", "SXG"))
    check_cbor = report.add(Check("Certificat CBOR", "SXG"))
    check_index = report.add(Check("index.cbor", "SXG"))
    check_headers = report.add(Check("Headers SXG", "SXG"))
    check_cdn = report.add(Check("CDN SXG", "SXG"))
    base = urlparse(url)
    try:
        r = requests.get(url, headers={"User-Agent": USER_AGENT, "Accept": "application/signed-exchange;v=b3,*/*;q=0.8"}, timeout=TIMEOUT, allow_redirects=True)
        if 'signed-exchange' in r.headers.get('content-type', ''):
            check_sxg.ok("SXG supporte")
            print_status("✅", "SXG: supporte")
        else:
            check_sxg.warn("SXG non detecte")
            print_status("⚠️", "SXG: non detecte")
    except Exception:
        check_sxg.warn("Test SXG impossible")
        print_status("⚠️", "SXG: test impossible")
    for path in ['/certificate.cbor', '/cert.cbor']:
        r = fetch_head(f"{base.scheme}://{base.netloc}{path}")
        if r and r.status_code == 200:
            check_cbor.ok(f"Certificat trouve a {path}")
            print_status("✅", f"CBOR cert: {path}")
            break
    else:
        check_cbor.warn("Pas de certificat CBOR")
        print_status("⚠️", "CBOR cert: absent")
    r = fetch(f"{base.scheme}://{base.netloc}/index.cbor")
    if r and r.status_code == 200 and 'html' not in r.headers.get('content-type', ''):
        check_index.ok(f"index.cbor present ({len(r.content)} octets)")
        print_status("✅", f"index.cbor: {len(r.content)} octets")
    else:
        check_index.warn("index.cbor absent")
        print_status("⚠️", "index.cbor: absent")
    check_headers.warn("Verification manuelle necessaire")
    print_status("⚠️", "Headers SXG: verification manuelle")
    r = fetch_head(url)
    server = r.headers.get('server', '').lower() if r else ""
    if 'cloudflare' in server:
        check_cdn.ok("Cloudflare detecte")
        print_status("✅", "CDN: Cloudflare")
    else:
        check_cdn.warn(f"Pas de Cloudflare (serveur: {server})")
        print_status("⚠️", f"CDN: {server or 'inconnu'}")
    return check_sxg

# ============================================================
# RAPPORT
# ============================================================

def print_report(report):
    print_section("RAPPORT FINAL")
    summary = report.summary()
    print(f"\n  Site: {report.url}")
    print(f"  Date: {report.timestamp}\n")
    labels = {"TECH": "1. Fondations techniques", "SEO": "2. Contenu & Autorite", "GEO": "3. Visibilite IA (GEO)", "SXG": "4. SXG / CBOR", "TOTAL": "TOTAL"}
    print(f"  {'Pilier':<30} {'OK':>4} {'/ Total':>8} {'Score':>8}")
    print(f"  {'-'*54}")
    for key in ["TECH", "SEO", "GEO", "SXG", "TOTAL"]:
        s = summary[key]
        bar = "█" * s["ok"] + "░" * (s["total"] - s["ok"])
        if key == "TOTAL": print(f"  {'-'*54}")
        print(f"  {labels[key]:<30} {s['ok']:>4} / {s['total']:<4} {s['pct']:>5}%  {bar}")
    priorities = report.priorities()
    if priorities:
        print(f"\n  TOP {min(5, len(priorities))} ACTIONS PRIORITAIRES:")
        print(f"  {'-'*54}")
        for i, (impact, check) in enumerate(priorities[:5], 1):
            icon = "🔴" if check.status == "ABSENT" else "🟠"
            print(f"  {i}. {icon} [{check.category}] {check.name}")
            print(f"     {check.detail[:80]}")
        print()

def save_json(report, filepath):
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\n  📁 Rapport JSON: {filepath}")

def save_html(report, filepath):
    data = report.to_dict()
    summary = data["summary"]
    status_colors = {"OK": "#006600", "A_CORRIGER": "#CC6600", "ABSENT": "#CC0000"}
    status_bg = {"OK": "#F0FFF0", "A_CORRIGER": "#FFFBE6", "ABSENT": "#FFF0F0"}
    rows = ""
    for check in data["checks"]:
        color = status_colors.get(check["status"], "#333")
        bg = status_bg.get(check["status"], "#FFF")
        rows += f'<tr><td>{check["category"]}</td><td>{check["name"]}</td><td style="background:{bg};color:{color};font-weight:bold;text-align:center">{check["status"]}</td><td style="font-size:13px">{check["detail"][:120]}</td></tr>\n'
    priority_rows = ""
    for i, p in enumerate(data["priorities"][:10], 1):
        icon = "🔴" if p["status"] == "ABSENT" else "🟠"
        priority_rows += f'<tr><td>{i}</td><td>{icon} [{p["category"]}]</td><td>{p["name"]}</td><td>{p["detail"][:100]}</td></tr>\n'
    html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Audit Web — {data['domain']}</title>
<style>body{{font-family:Arial,sans-serif;max-width:1100px;margin:0 auto;padding:20px;background:#fafafa;color:#333}}h1{{color:#1B4332;border-bottom:3px solid #2D6A4F;padding-bottom:10px}}h2{{color:#2D6A4F;margin-top:30px}}table{{width:100%;border-collapse:collapse;margin:15px 0;font-size:14px}}th{{background:#1B4332;color:#fff;padding:10px;text-align:left}}td{{padding:8px 10px;border:1px solid #ddd}}tr:nth-child(even){{background:#f9f9f9}}.score-box{{display:inline-block;padding:8px 16px;border-radius:8px;font-weight:bold;font-size:18px;margin:5px}}.score-good{{background:#F0FFF0;color:#006600}}.score-warn{{background:#FFFBE6;color:#CC6600}}.score-bad{{background:#FFF0F0;color:#CC0000}}.meta{{color:#999;font-size:14px}}</style></head><body>
<h1>Audit Visibilite Web</h1>
<p class="meta">Site: <strong>{data['url']}</strong> | Date: {data['timestamp']}</p>
<h2>Scores</h2><div>
<span class="score-box {'score-good' if summary['TECH']['pct']>=70 else 'score-warn' if summary['TECH']['pct']>=40 else 'score-bad'}">Tech: {summary['TECH']['ok']}/{summary['TECH']['total']}</span>
<span class="score-box {'score-good' if summary['SEO']['pct']>=70 else 'score-warn' if summary['SEO']['pct']>=40 else 'score-bad'}">SEO: {summary['SEO']['ok']}/{summary['SEO']['total']}</span>
<span class="score-box {'score-good' if summary['GEO']['pct']>=70 else 'score-warn' if summary['GEO']['pct']>=40 else 'score-bad'}">GEO: {summary['GEO']['ok']}/{summary['GEO']['total']}</span>
<span class="score-box {'score-good' if summary['SXG']['pct']>=70 else 'score-warn' if summary['SXG']['pct']>=40 else 'score-bad'}">SXG: {summary['SXG']['ok']}/{summary['SXG']['total']}</span>
<span class="score-box {'score-good' if summary['TOTAL']['pct']>=60 else 'score-warn' if summary['TOTAL']['pct']>=35 else 'score-bad'}">TOTAL: {summary['TOTAL']['ok']}/{summary['TOTAL']['total']} ({summary['TOTAL']['pct']}%)</span></div>
<h2>Actions prioritaires</h2><table><tr><th>#</th><th>Pilier</th><th>Point</th><th>Detail</th></tr>{priority_rows}</table>
<h2>Detail</h2><table><tr><th>Pilier</th><th>Verification</th><th>Statut</th><th>Detail</th></tr>{rows}</table>
<p class="meta">Deltopide Web Audit Tool v1.0</p></body></html>"""
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"\n  📁 Rapport HTML: {filepath}")

# ============================================================
# ORCHESTRATEUR
# ============================================================

def run_audit(url):
    if not url.startswith('http'):
        url = 'https://' + url
    report = AuditReport(url)
    print(f"\n{'='*60}")
    print(f"  DELTOPIDE WEB AUDIT TOOL v1.0")
    print(f"{'='*60}")
    print(f"\n  Cible: {url}")
    print_section("PILIER 1 : FONDATIONS TECHNIQUES")
    start_time = time.time()
    response = fetch(url)
    response_time = time.time() - start_time
    if not response or response.status_code != 200:
        print(f"\n  ❌ ERREUR: Site inaccessible (HTTP {response.status_code if response else 'timeout'})")
        return report
    html_content = response.text
    html_size = len(response.content)
    soup = BeautifulSoup(html_content, 'html.parser')
    audit_ssr(report, url, html_content, html_size)
    audit_sitemap(report, url)
    audit_robots(report, url)
    audit_meta_tags(report, soup, html_content)
    audit_open_graph(report, soup)
    audit_schema(report, soup, html_content)
    audit_performance(report, url, response_time)
    audit_https(report, url)
    audit_mobile(report, soup)
    print_section("PILIER 2 : CONTENU & AUTORITE SEO")
    audit_content_volume(report, url)
    audit_headings(report, soup)
    audit_mentions_legales(report, url, soup)
    audit_eeat(report, soup)
    print_section("PILIER 3 : VISIBILITE IA (GEO)")
    audit_geo_content_structure(report, soup, html_content)
    audit_geo_citable_data(report, soup)
    print_section("PILIER 4 : SXG / CBOR")
    audit_sxg(report, url)
    print_report(report)
    return report

def main():
    parser = argparse.ArgumentParser(description="Deltopide Web Audit Tool v1.0")
    parser.add_argument('urls', nargs='+', help='URL(s) a auditer')
    parser.add_argument('--output', '-o', help='Fichier de sortie')
    parser.add_argument('--format', '-f', choices=['json', 'html'], default='json')
    args = parser.parse_args()
    all_reports = []
    for url in args.urls:
        report = run_audit(url)
        all_reports.append(report)
        if len(args.urls) == 1 and args.output:
            if args.format == 'html': save_html(report, args.output)
            else: save_json(report, args.output)
    if len(args.urls) > 1 and args.output:
        combined = {"timestamp": datetime.now().isoformat(), "sites": [r.to_dict() for r in all_reports]}
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(combined, f, ensure_ascii=False, indent=2)
        print(f"\n  📁 Rapport combine: {args.output}")
    if not args.output:
        for report in all_reports:
            domain = report.domain.replace('www.', '').replace('.', '_')
            ts = datetime.now().strftime('%Y%m%d')
            save_json(report, f"audit_{domain}_{ts}.json")
            save_html(report, f"audit_{domain}_{ts}.html")

if __name__ == "__main__":
    main()
