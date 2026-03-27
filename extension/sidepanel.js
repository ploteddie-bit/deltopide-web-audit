// ============================================================
// DELTOPIDE WEB AUDIT — Side Panel Controller
// ============================================================

const app = document.getElementById("app");
let currentResult = null;

async function init() {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.url || tab.url.startsWith("chrome://")) {
    app.innerHTML = `
      <div class="header">
        <div class="header-brand">
          <div class="header-logo">D</div>
          <div class="header-title"><span>Deltopide</span> Audit</div>
        </div>
      </div>
      <div class="idle">
        <div class="idle-icon">🚫</div>
        <div class="idle-text">Naviguez vers un site web pour lancer un audit.</div>
      </div>
    `;
    return;
  }

  // Check cache
  const cached = await chrome.storage.session.get(tab.url);
  if (cached[tab.url]) {
    currentResult = cached[tab.url];
    showResult();
  } else {
    showIdle(tab);
  }
}

function showIdle(tab) {
  app.innerHTML = `
    <div class="header">
      <div class="header-brand">
        <div class="header-logo">D</div>
        <div class="header-title"><span>Deltopide</span> Audit</div>
      </div>
      <div class="header-url">${escapeHtml(tab.url)}</div>
    </div>
    ${renderIdle("sidepanel")}
  `;

  document.getElementById("btn-audit").addEventListener("click", () => runAudit(tab));
}

async function runAudit(tab) {
  if (!tab) {
    const [t] = await chrome.tabs.query({ active: true, currentWindow: true });
    tab = t;
  }

  app.innerHTML = `
    <div class="header">
      <div class="header-brand">
        <div class="header-logo">D</div>
        <div class="header-title"><span>Deltopide</span> Audit</div>
      </div>
      <div class="header-url">${escapeHtml(tab.url)}</div>
    </div>
    ${renderLoading()}
  `;

  try {
    // Inject content script
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      files: ["content.js"]
    });

    await new Promise(r => setTimeout(r, 200));

    // Get DOM data
    const domResponse = await chrome.tabs.sendMessage(tab.id, { action: "analyzeDOM" });
    if (!domResponse?.success) throw new Error(domResponse?.error || "DOM analysis failed");

    // Run full audit
    const result = await chrome.runtime.sendMessage({
      action: "runFullAudit",
      url: tab.url,
      domData: domResponse.data
    });

    currentResult = result;
    await chrome.storage.session.set({ [tab.url]: result });

    showResult();
  } catch (err) {
    app.innerHTML = `
      <div class="header">
        <div class="header-brand">
          <div class="header-logo">D</div>
          <div class="header-title"><span>Deltopide</span> Audit</div>
        </div>
      </div>
      <div class="idle">
        <div class="idle-icon">⚠️</div>
        <div class="idle-text">Erreur: ${escapeHtml(err.message)}</div>
        <button class="btn btn-primary" id="btn-retry">Réessayer</button>
      </div>
    `;
    document.getElementById("btn-retry")?.addEventListener("click", () => runAudit(tab));
  }
}

function showResult() {
  app.innerHTML = renderFullReport(currentResult, "sidepanel");

  document.getElementById("btn-export")?.addEventListener("click", () => {
    exportJSON(currentResult);
  });

  document.getElementById("btn-export-csv")?.addEventListener("click", () => {
    exportCSV(currentResult);
  });

  document.getElementById("btn-reaudit")?.addEventListener("click", async () => {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    runAudit(tab);
  });
}

// Listen for tab changes
chrome.tabs.onActivated?.addListener(async () => {
  await init();
});

chrome.tabs.onUpdated?.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "complete") {
    init();
  }
});

init();
