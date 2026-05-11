# HanaFi Ripple Engine Prototype

FastAPI service for working with the XRP Ledger on testnet or mainnet, with a simple web UI for wallet creation, wallet details, XRP transfers, transaction lookup, and paginated transaction history.

## What This Demo Does

- Browser-based frontend at `/ui` — no Swagger required for basic testing
- Creates XRPL wallets (faucet-funded on testnet, keypair-only on mainnet)
- Shows wallet details: address, balance, sequence, ledger index
- Sends XRP between wallets with optional on-chain memos
- Returns transaction hash, ledger result, and XRPL explorer URL
- Checks transaction status by hash
- Paginated wallet transaction history with direction, counterparty, amount, fee, result, date, memo, and explorer links
- Supports testnet and mainnet via a single `XRPL_NETWORK` env var

## What This Demo Does Not Do

- Does not use real funds (testnet only by default)
- Does not store private keys securely for production
- Does not integrate external banking or payout providers
- Does not implement RLUSD or issued token trust lines

## Why XRP Instead of RLUSD?

XRP is the native asset of the XRP Ledger — the simplest first demo. RLUSD can be added later as an issued stablecoin flow, but requires issuer and trust-line handling.

## Setup

```bash
git clone https://github.com/humblebeeai-academy/hanafi-ripple-engine.git
cd hanafi-ripple-engine
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload
```

Open the frontend: http://127.0.0.1:8000/ui

API docs (Swagger): http://127.0.0.1:8000/docs

## Docker

```bash
docker compose up
```

## Configuration

Copy `.env.example` to `.env` and set:

| Variable | Default | Description |
|----------|---------|-------------|
| `XRPL_NETWORK` | `testnet` | `testnet` or `mainnet` |
| `XRPL_JSON_RPC_URL` | *(auto)* | Override RPC endpoint |
| `XRPL_EXPLORER_TX_URL` | *(auto)* | Override explorer URL template |
| `FAUCET_USAGE_CONTEXT` | `hanafi-ripple-engine-demo` | Label sent to testnet faucet |

RPC URL and explorer URL default automatically based on `XRPL_NETWORK`. Override only if pointing at a custom node.

## API Reference

**Health check**
```bash
curl http://localhost:8000/
```

**Create and fund a testnet wallet**
```bash
curl -X POST http://localhost:8000/ripple/wallets \
  -H "Content-Type: application/json" \
  -d '{"fund": true}'
```

**Create an unfunded wallet (works on mainnet)**
```bash
curl -X POST http://localhost:8000/ripple/wallets \
  -H "Content-Type: application/json" \
  -d '{"fund": false}'
```

**Get account info**
```bash
curl http://localhost:8000/ripple/accounts/{address}
```

**Send XRP**
```bash
curl -X POST http://localhost:8000/ripple/payments/xrp \
  -H "Content-Type: application/json" \
  -d '{
    "source_seed": "sn...",
    "destination_address": "r...",
    "amount_xrp": "10.50",
    "memo": "invoice-ORD-0041"
  }'
```

**Check transaction status**
```bash
curl http://localhost:8000/ripple/payments/{tx_hash}
```

**Wallet transaction history**
```bash
# First page
curl "http://localhost:8000/ripple/accounts/{address}/transactions?limit=10"

# Next page (pass next_marker from previous response)
curl "http://localhost:8000/ripple/accounts/{address}/transactions?limit=10&marker={next_marker}"
```

## Error Codes

| Code | Meaning |
|------|---------|
| `422` | Invalid XRPL address format |
| `404` | Account or transaction not found on the network |
| `400` | Bad request (e.g. faucet requested on mainnet) |
| `502` | XRPL network error |

## Live Demo (Testnet)

Merchant wallet with 13 transactions across 3 counterparties:
- Address: `rKtg7ydmLu2dXrXzKKsvYBAXTJfeUe2erN`
- Explorer: https://testnet.xrpl.org/accounts/rKtg7ydmLu2dXrXzKKsvYBAXTJfeUe2erN

## Production Notes

Before any production usage:

- Never return or store seeds in API responses — use HSM/MPC or a dedicated signer service
- Add destination allowlists and per-transaction limits
- Store all transactions in a database with idempotency keys
- Wait for `validated: true` in ledger results before marking settlement complete
- Add auth and rate limiting before exposing publicly
- Add RLUSD only after issuer, trust-line, liquidity, and compliance reviews
