// ============================================================
// DELTOPIDE WEB AUDIT v1.2 — Background Service Worker
// Moteur Rust/WASM — Wrapper JS leger
// Copyright (c) 2026 Deltopide SL
// ============================================================

import init, { run_audit, validate_license, get_version } from "./audit_engine.js";

let wasmReady = false;
let _auditCount = 0;
let _auditWindowStart = Date.now();

// Initialize WASM on load
async function initWasm() {
  try {
    await init();
    wasmReady = true;
    console.log(`[Deltopide] Moteur WASM ${get_version()} charge`);
  } catch (e) {
    console.error("[Deltopide] Erreur chargement WASM:", e);
  }
}

initWasm();

// Side panel behavior
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: false });
});

// Rate limiting
function checkRateLimit() {
  const now = Date.now();
  if (now - _auditWindowStart > 60000) { _auditCount = 0; _auditWindowStart = now; }
  return ++_auditCount <= 30;
}

// License check via WASM
async function checkLicense() {
  const store = await chrome.storage.local.get(["deltopide_license"]);
  const key = store.deltopide_license || "";
  if (!key) return { valid: false, reason: "no_key" };
  if (new Date() > new Date("2027-03-27")) return { valid: false, reason: "expired" };
  if (!wasmReady) return { valid: false, reason: "wasm_loading" };
  const valid = validate_license(key);
  return { valid, reason: valid ? "ok" : "invalid_key" };
}

// Fetch helpers
async function fetchText(url) {
  try {
    const r = await fetch(url, { method: "GET", headers: { "User-Agent": "DeltopideAudit/1.2" } });
    if (r.ok) return { ok: true, text: await r.text(), status: r.status };
    return { ok: false, status: r.status };
  } catch (e) { return { ok: false, status: 0 }; }
}

async function fetchBinary(url) {
  try {
    const r = await fetch(url, { method: "GET" });
    if (r.ok) { const buf = await r.arrayBuffer(); return { ok: true, size: buf.byteLength, status: r.status }; }
    return { ok: false, status: r.status };
  } catch (e) { return { ok: false, status: 0 }; }
}

async function fetchHead(url) {
  try {
    const r = await fetch(url, { method: "HEAD" });
    const headers = {};
    r.headers.forEach((v, k) => { headers[k.toLowerCase()] = v; });
    return { ok: true, status: r.status, headers };
  } catch (e) { return { ok: false, status: 0, headers: {} }; }
}

// Message handler
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (msg.action === "runFullAudit") {
    (async () => {
      const license = await checkLicense();
      if (!license.valid) {
        sendResponse({ error: "licence_invalide", reason: license.reason,
          message: "Activez votre licence Deltopide." });
        return;
      }
      if (!wasmReady) {
        sendResponse({ error: "wasm_loading", message: "Moteur en cours de chargement. Reessayez." });
        return;
      }
      if (!checkRateLimit()) {
        sendResponse({ error: "rate_limit", message: "Trop de requetes." });
        return;
      }

      // Fetch external resources
      const origin = new URL(msg.url).origin;
      const [robotsData, sitemapData, cborData, headData, llmsData] = await Promise.all([
        fetchText(`${origin}/robots.txt`),
        fetchText(`${origin}/sitemap.xml`),
        fetchBinary(`${origin}/index.cbor`),
        fetchHead(msg.url),
        fetchText(`${origin}/llms.txt`)
      ]);

      const fetchResults = {
        robots_ok: robotsData.ok || false,
        robots_text: robotsData.text || "",
        sitemap_ok: sitemapData.ok || false,
        sitemap_text: sitemapData.text || "",
        cbor_ok: cborData.ok || false,
        cbor_size: cborData.size || 0,
        cbor_status: cborData.status || 0,
        head_ok: headData.ok || false,
        head_headers: headData.headers || {},
        llms_ok: llmsData.ok || false,
        llms_text: llmsData.text || ""
      };

      // Convert camelCase → snake_case for Rust
      const dom = msg.domData;
      const domForRust = {
        url: msg.url, domain: dom.domain || "",
        is_https: dom.isHTTPS || false,
        title: (dom.title || "").substring(0, 2000),
        title_length: dom.titleLength || 0,
        meta_desc: (dom.metaDesc || "").substring(0, 2000),
        meta_desc_length: dom.metaDescLength || 0,
        canonical: (dom.canonical || "").substring(0, 2000),
        canonical_mismatch: dom.canonicalMismatch || false,
        canonical_domain_mismatch: dom.canonicalDomainMismatch || false,
        canonical_domain: dom.canonicalDomain || "",
        viewport: dom.viewport || "", lang: dom.lang || "",
        html_size: dom.htmlSize || 0, word_count: dom.wordCount || 0,
        is_spa: dom.isSPA || false, has_favicon: dom.hasFavicon || false,
        last_modified_meta: dom.lastModifiedMeta || "",
        article_date: dom.articleDate || "",
        has_skip_link: dom.hasSkipLink || false,
        aria_landmarks: dom.ariaLandmarks || 0,
        has_llms_txt_link: dom.hasLlmsTxtLink || false,
        headings: dom.headings || { h1: [], h2: [], h3: [] },
        og: dom.og || {},
        schemas: (dom.schemas || []).map(s => ({ type: s.type || "", name: s.name || "" })),
        hreflangs: dom.hreflangs || [],
        images_total: dom.imagesTotal || 0,
        images_without_alt: dom.imagesWithoutAlt || 0,
        internal_links_count: dom.internalLinksCount || 0,
        external_links_count: dom.externalLinksCount || 0,
        social_links: dom.socialLinks || [],
        tables: dom.tables || 0, lists: dom.lists || 0,
        definition_lists: dom.definitionLists || 0,
        blockquotes: dom.blockquotes || 0,
        stats_found: dom.statsFound || 0,
        faq_patterns: dom.faqPatterns || 0,
        has_about_page: dom.hasAboutPage || false,
        has_contact_page: dom.hasContactPage || false,
        has_privacy_page: dom.hasPrivacyPage || false,
        has_author_info: dom.hasAuthorInfo || false,
        has_testimonials: dom.hasTestimonials || false,
        cwv: dom.cwv || {}, perf_data: dom.perfData || {}
      };

      // WASM engine call
      const resultJson = run_audit(JSON.stringify(domForRust), JSON.stringify(fetchResults));
      const result = JSON.parse(resultJson);
      result.timestamp = new Date().toISOString();
      result._build = get_version();
      result._licensed = "full";

      sendResponse(result);
    })();
    return true;
  }

  if (msg.action === "openSidePanel") {
    chrome.sidePanel.open({ tabId: msg.tabId });
    return false;
  }

  if (msg.action === "activateLicense") {
    (async () => {
      await chrome.storage.local.set({ deltopide_license: msg.key });
      const result = await checkLicense();
      sendResponse(result);
    })();
    return true;
  }

  if (msg.action === "checkLicense") {
    checkLicense().then(sendResponse);
    return true;
  }
});
