const els = {
  healthText: document.getElementById("healthText"),
  healthDot: document.getElementById("healthDot"),
  toast: document.getElementById("toast"),
  fundWallet: document.getElementById("fundWallet"),
  createWalletBtn: document.getElementById("createWalletBtn"),
  walletAddress: document.getElementById("walletAddress"),
  walletSeed: document.getElementById("walletSeed"),
  walletPubKey: document.getElementById("walletPubKey"),
  walletFunded: document.getElementById("walletFunded"),
  toggleSeedBtn: document.getElementById("toggleSeedBtn"),
  accountAddress: document.getElementById("accountAddress"),
  loadAccountBtn: document.getElementById("loadAccountBtn"),
  accountDetailAddress: document.getElementById("accountDetailAddress"),
  accountBalance: document.getElementById("accountBalance"),
  accountSequence: document.getElementById("accountSequence"),
  accountLedger: document.getElementById("accountLedger"),
  sendSourceSeed: document.getElementById("sendSourceSeed"),
  sendDestAddress: document.getElementById("sendDestAddress"),
  sendAmount: document.getElementById("sendAmount"),
  sendMemo: document.getElementById("sendMemo"),
  sendXrpBtn: document.getElementById("sendXrpBtn"),
  sendTxHash: document.getElementById("sendTxHash"),
  sendResult: document.getElementById("sendResult"),
  sendValidated: document.getElementById("sendValidated"),
  sendExplorer: document.getElementById("sendExplorer"),
  copyTxHashBtn: document.getElementById("copyTxHashBtn"),
  checkTxHash: document.getElementById("checkTxHash"),
  checkTxBtn: document.getElementById("checkTxBtn"),
  checkValidated: document.getElementById("checkValidated"),
  checkResult: document.getElementById("checkResult"),
  checkLedger: document.getElementById("checkLedger"),
  checkExplorer: document.getElementById("checkExplorer"),
  historyAddress: document.getElementById("historyAddress"),
  historyLimit: document.getElementById("historyLimit"),
  loadHistoryBtn: document.getElementById("loadHistoryBtn"),
  copyHistoryJsonBtn: document.getElementById("copyHistoryJsonBtn"),
  historySummary: document.getElementById("historySummary"),
  historyList: document.getElementById("historyList"),
  rawJson: document.getElementById("rawJson"),
  copyRawBtn: document.getElementById("copyRawBtn"),
  clearRawBtn: document.getElementById("clearRawBtn"),
};

let lastSeed = null;
let seedVisible = false;
let toastTimer = null;
let lastHistory = null;
let lastAccount = null;

function setHealth(ok, text) {
  els.healthText.textContent = text;
  els.healthDot.style.background = ok ? "rgba(70, 230, 168, 0.95)" : "rgba(255, 90, 106, 0.95)";
}

function setRaw(obj) {
  els.rawJson.textContent = JSON.stringify(obj, null, 2);
}

function toast(message) {
  if (!els.toast) return;
  els.toast.textContent = message;
  els.toast.classList.add("show");
  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    els.toast.classList.remove("show");
  }, 1600);
}

function maskSeed(seed) {
  if (!seed) return "-";
  if (seed.length <= 10) return "**********";
  return `${seed.slice(0, 4)}...${seed.slice(-4)}`;
}

function renderSeed() {
  els.walletSeed.textContent = seedVisible ? (lastSeed || "-") : maskSeed(lastSeed);
}

function shortHash(value) {
  if (!value) return "-";
  if (value.length <= 18) return value;
  return `${value.slice(0, 10)}...${value.slice(-8)}`;
}

function formatXrp(value) {
  if (value === null || value === undefined || value === "") return "-";
  return `${value} XRP`;
}

function formatDate(value) {
  if (!value) return "-";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString();
}

function renderHistory(data) {
  lastHistory = data;
  const txs = data.transactions || [];
  els.historySummary.textContent = `${txs.length} transaction(s) loaded for ${data.address}`;

  if (!txs.length) {
    els.historyList.innerHTML = '<div class="emptyState">No transactions found for this wallet.</div>';
    return;
  }

  els.historyList.innerHTML = txs
    .map((tx, index) => {
      const explorer = tx.explorer_url || "#";
      return `
        <article class="historyItem">
          <div class="historyTop">
            <span class="pill ${tx.direction || "other"}">${tx.direction || "other"}</span>
            <span class="mono">${shortHash(tx.tx_hash)}</span>
            <button class="btn mini" data-history-copy="${index}" data-history-field="tx_hash">Copy hash</button>
          </div>
          <div class="historyGrid">
            <div><span>Type</span><strong>${tx.transaction_type || "-"}</strong></div>
            <div><span>Result</span><strong>${tx.result || "-"}</strong></div>
            <div><span>Validated</span><strong>${String(!!tx.validated)}</strong></div>
            <div><span>Amount</span><strong>${formatXrp(tx.amount_xrp)}</strong></div>
            <div><span>Fee</span><strong>${formatXrp(tx.fee_xrp)}</strong></div>
            <div><span>Ledger</span><strong>${tx.ledger_index ?? "-"}</strong></div>
            <div><span>Date</span><strong>${formatDate(tx.date)}</strong></div>
            <div><span>Memo</span><strong>${tx.memo || "-"}</strong></div>
          </div>
          <div class="historyCounterparty">
            <span>Counterparty</span>
            <strong class="mono">${tx.counterparty || "-"}</strong>
          </div>
          <div class="historyActions">
            <a href="${explorer}" target="_blank" rel="noreferrer">Open explorer</a>
            <button class="btn mini" data-history-copy="${index}" data-history-field="explorer_url">Copy explorer</button>
          </div>
        </article>
      `;
    })
    .join("");
}

async function copyText(text) {
  const value = String(text || "").trim();
  if (!value || value === "-") {
    toast("Nothing to copy");
    return;
  }

  try {
    await navigator.clipboard.writeText(value);
    toast("Copied");
  } catch (e) {
    const ta = document.createElement("textarea");
    ta.value = value;
    ta.setAttribute("readonly", "");
    ta.style.position = "fixed";
    ta.style.left = "-9999px";
    document.body.appendChild(ta);
    ta.select();
    try {
      document.execCommand("copy");
      toast("Copied");
    } catch {
      toast("Copy failed");
    } finally {
      document.body.removeChild(ta);
    }
  }
}

async function apiFetch(path, options) {
  const res = await fetch(path, options);
  const body = await res.json().catch(() => ({}));
  if (!res.ok) {
    const msg = body?.detail || body?.error || `HTTP ${res.status}`;
    throw new Error(msg);
  }
  return body;
}

async function health() {
  try {
    const data = await apiFetch("/");
    setHealth(true, `${data.status} (${data.network})`);
    setRaw(data);
  } catch (e) {
    setHealth(false, `API error: ${e.message}`);
  }
}

els.toggleSeedBtn.addEventListener("click", () => {
  seedVisible = !seedVisible;
  renderSeed();
  toast(seedVisible ? "Seed visible" : "Seed hidden");
});

els.createWalletBtn.addEventListener("click", async () => {
  els.createWalletBtn.disabled = true;
  els.createWalletBtn.textContent = "Creating...";
  try {
    const payload = { fund: !!els.fundWallet.checked };
    const data = await apiFetch("/ripple/wallets", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    els.walletAddress.textContent = data.classic_address || "-";
    lastSeed = data.seed || null;
    renderSeed();
    els.walletPubKey.textContent = data.public_key || "-";
    els.walletFunded.textContent = String(!!data.funded);

    setRaw(data);
    toast("Wallet created");
  } catch (e) {
    setRaw({ error: e.message });
    toast(e.message);
  } finally {
    els.createWalletBtn.disabled = false;
    els.createWalletBtn.textContent = "Create Wallet";
  }
});

els.loadAccountBtn.addEventListener("click", async () => {
  els.loadAccountBtn.disabled = true;
  els.loadAccountBtn.textContent = "Loading...";
  try {
    const address = els.accountAddress.value.trim();
    const data = await apiFetch(`/ripple/accounts/${encodeURIComponent(address)}`);

    lastAccount = data;
    els.accountDetailAddress.textContent = data.address || "-";
    els.accountBalance.textContent = data.balance_xrp ? `${data.balance_xrp} XRP` : "-";
    els.accountSequence.textContent = String(data.sequence ?? "-");
    els.accountLedger.textContent = String(data.ledger_index ?? "-");
    setRaw(data);
    toast("Account loaded");
  } catch (e) {
    lastAccount = null;
    els.accountDetailAddress.textContent = "-";
    els.accountBalance.textContent = "-";
    els.accountSequence.textContent = "-";
    els.accountLedger.textContent = "-";
    setRaw({ error: e.message });
    toast(e.message);
  } finally {
    els.loadAccountBtn.disabled = false;
    els.loadAccountBtn.textContent = "Load details";
  }
});

els.loadHistoryBtn.addEventListener("click", async () => {
  els.loadHistoryBtn.disabled = true;
  els.loadHistoryBtn.textContent = "Loading...";
  try {
    const address = els.historyAddress.value.trim();
    const limit = encodeURIComponent(els.historyLimit.value.trim() || "20");
    const data = await apiFetch(
      `/ripple/accounts/${encodeURIComponent(address)}/transactions?limit=${limit}`,
    );

    renderHistory(data);
    setRaw(data);
    toast("History loaded");
  } catch (e) {
    lastHistory = null;
    els.historySummary.textContent = "History failed to load.";
    els.historyList.innerHTML = `<div class="emptyState">${e.message}</div>`;
    setRaw({ error: e.message });
    toast(e.message);
  } finally {
    els.loadHistoryBtn.disabled = false;
    els.loadHistoryBtn.textContent = "Load history";
  }
});

els.sendXrpBtn.addEventListener("click", async () => {
  els.sendXrpBtn.disabled = true;
  els.sendXrpBtn.textContent = "Sending...";
  try {
    const payload = {
      source_seed: els.sendSourceSeed.value.trim(),
      destination_address: els.sendDestAddress.value.trim(),
      amount_xrp: els.sendAmount.value.trim(),
      memo: els.sendMemo.value.trim() || null,
    };
    const data = await apiFetch("/ripple/payments/xrp", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    els.sendTxHash.textContent = data.tx_hash || "-";
    els.sendResult.textContent = data.engine_result || "-";
    els.sendValidated.textContent = String(!!data.validated);

    if (data.explorer_url) {
      els.sendExplorer.href = data.explorer_url;
      els.sendExplorer.textContent = data.explorer_url;
    } else {
      els.sendExplorer.href = "#";
      els.sendExplorer.textContent = "-";
    }

    els.checkTxHash.value = data.tx_hash || "";
    setRaw(data);
    toast("Payment sent");
  } catch (e) {
    setRaw({ error: e.message });
    toast(e.message);
  } finally {
    els.sendXrpBtn.disabled = false;
    els.sendXrpBtn.textContent = "Send XRP";
  }
});

els.checkTxBtn.addEventListener("click", async () => {
  els.checkTxBtn.disabled = true;
  els.checkTxBtn.textContent = "Checking...";
  try {
    const txHash = els.checkTxHash.value.trim();
    const data = await apiFetch(`/ripple/payments/${encodeURIComponent(txHash)}`);

    els.checkValidated.textContent = String(!!data.validated);
    els.checkResult.textContent = data.engine_result || "-";
    els.checkLedger.textContent = String(data.ledger_index ?? "-");

    if (data.explorer_url) {
      els.checkExplorer.href = data.explorer_url;
      els.checkExplorer.textContent = data.explorer_url;
    } else {
      els.checkExplorer.href = "#";
      els.checkExplorer.textContent = "-";
    }

    setRaw(data);
    toast("Status loaded");
  } catch (e) {
    setRaw({ error: e.message });
    toast(e.message);
  } finally {
    els.checkTxBtn.disabled = false;
    els.checkTxBtn.textContent = "Check Status";
  }
});

function setActivePage(page) {
  document.querySelectorAll(".navItem").forEach((b) => b.classList.remove("active"));
  document.querySelectorAll(".page").forEach((p) => p.classList.remove("active"));
  const nav = document.querySelector(`.navItem[data-page="${page}"]`);
  const section = document.querySelector(`.page[data-page="${page}"]`);
  if (nav) nav.classList.add("active");
  if (section) section.classList.add("active");
  history.replaceState(null, "", `#${page}`);
}

document.querySelectorAll(".navItem").forEach((btn) => {
  btn.addEventListener("click", () => setActivePage(btn.dataset.page));
});

function getCopyValue(targetId) {
  if (targetId === "walletSeed") return seedVisible ? (lastSeed || "") : (lastSeed || "");
  if (targetId === "sendExplorer") return els.sendExplorer?.textContent || "";
  if (targetId === "checkExplorer") return els.checkExplorer?.textContent || "";
  if (targetId === "rawJson") return els.rawJson?.textContent || "";
  const el = document.getElementById(targetId);
  if (el && el.tagName === "INPUT") return el.value || "";
  return el ? el.textContent || "" : "";
}

document.addEventListener("click", (e) => {
  const btn = e.target?.closest?.("[data-copy]");
  if (!btn) return;
  const targetId = btn.getAttribute("data-copy");
  const value = getCopyValue(targetId);
  copyText(value);
});

document.addEventListener("click", (e) => {
  const btn = e.target?.closest?.("[data-history-copy]");
  if (!btn || !lastHistory) return;
  const index = Number(btn.getAttribute("data-history-copy"));
  const field = btn.getAttribute("data-history-field");
  const tx = lastHistory.transactions?.[index];
  copyText(tx?.[field] || "");
});

if (els.copyHistoryJsonBtn) {
  els.copyHistoryJsonBtn.addEventListener("click", () => {
    copyText(lastHistory ? JSON.stringify(lastHistory, null, 2) : "");
  });
}

if (els.copyRawBtn) {
  els.copyRawBtn.addEventListener("click", () => copyText(getCopyValue("rawJson")));
}

if (els.clearRawBtn) {
  els.clearRawBtn.addEventListener("click", () => {
    setRaw({});
    toast("Cleared");
  });
}

const initialPage = (location.hash || "#wallets").replace("#", "");
setActivePage(initialPage);
health();
