const els = {
  healthText: document.getElementById("healthText"),
  healthDot: document.getElementById("healthDot"),
  fundWallet: document.getElementById("fundWallet"),
  createWalletBtn: document.getElementById("createWalletBtn"),
  walletAddress: document.getElementById("walletAddress"),
  walletSeed: document.getElementById("walletSeed"),
  walletPubKey: document.getElementById("walletPubKey"),
  walletFunded: document.getElementById("walletFunded"),
  toggleSeedBtn: document.getElementById("toggleSeedBtn"),
  sendSourceSeed: document.getElementById("sendSourceSeed"),
  sendDestAddress: document.getElementById("sendDestAddress"),
  sendAmount: document.getElementById("sendAmount"),
  sendMemo: document.getElementById("sendMemo"),
  sendXrpBtn: document.getElementById("sendXrpBtn"),
  sendTxHash: document.getElementById("sendTxHash"),
  sendResult: document.getElementById("sendResult"),
  sendValidated: document.getElementById("sendValidated"),
  sendExplorer: document.getElementById("sendExplorer"),
  checkTxHash: document.getElementById("checkTxHash"),
  checkTxBtn: document.getElementById("checkTxBtn"),
  checkValidated: document.getElementById("checkValidated"),
  checkResult: document.getElementById("checkResult"),
  checkLedger: document.getElementById("checkLedger"),
  checkExplorer: document.getElementById("checkExplorer"),
  rawJson: document.getElementById("rawJson"),
};

let lastSeed = null;
let seedVisible = false;

function setHealth(ok, text) {
  els.healthText.textContent = text;
  els.healthDot.style.background = ok ? "rgba(70, 230, 168, 0.95)" : "rgba(255, 90, 106, 0.95)";
}

function setRaw(obj) {
  els.rawJson.textContent = JSON.stringify(obj, null, 2);
}

function maskSeed(seed) {
  if (!seed) return "-";
  if (seed.length <= 10) return "**********";
  return `${seed.slice(0, 4)}...${seed.slice(-4)}`;
}

function renderSeed() {
  els.walletSeed.textContent = seedVisible ? (lastSeed || "-") : maskSeed(lastSeed);
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

    if (data.funded) {
      els.sendSourceSeed.value = data.seed || "";
    } else {
      els.sendDestAddress.value = data.classic_address || "";
    }

    setRaw(data);
  } catch (e) {
    setRaw({ error: e.message });
  } finally {
    els.createWalletBtn.disabled = false;
    els.createWalletBtn.textContent = "Create Wallet";
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
  } catch (e) {
    setRaw({ error: e.message });
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
  } catch (e) {
    setRaw({ error: e.message });
  } finally {
    els.checkTxBtn.disabled = false;
    els.checkTxBtn.textContent = "Check Status";
  }
});

health();

