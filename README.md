# HanaFi Ripple Engine Prototype

Small FastAPI service for working with Ripple/XRPL on testnet, with a simple web UI for wallet creation, XRP transfer, and transaction lookup.

## Purpose

This service provides a minimal Ripple/XRPL codebase that:

- includes a browser-based frontend at `/ui`
- creates XRPL testnet wallets
- funds testnet wallets from faucet
- sends XRP from one wallet to another
- returns transaction hash, ledger result, and explorer URL
- checks transaction status by hash

## What This Demo Does

- Provides a simple frontend at `/ui` so wallet-to-wallet transfers can be tested without Swagger.
- Creates XRPL testnet wallets.
- Optionally funds a testnet wallet from the XRPL faucet.
- Sends XRP from one testnet wallet to another.
- Returns the transaction hash, ledger result, and explorer URL.
- Checks transaction status by hash.

## What This Demo Does Not Do

- It does not use real funds.
- It does not integrate external banking or payout providers.
- It does not store private keys securely for production.
- It does not implement RLUSD or issued token trust lines yet.

## Why XRP Instead of RLUSD?

The requested prototype focuses on "Ripple's coin" moving from one wallet to
another. In XRPL terminology, that means XRP. XRP is the native asset of the XRP
Ledger, so it is the simplest and safest first demo. RLUSD can be added later as
an issued stablecoin flow, but it requires issuer and trust-line handling.

## Setup

```bash
git clone https://github.com/humblebeeai-academy/hanafi-ripple-engine.git
cd hanafi-ripple-engine
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
cp .env.example .env
uvicorn app.main:app --reload --port 8088
```

Open the frontend:

```text
http://127.0.0.1:8088/ui
```

Optional API docs:

```text
http://127.0.0.1:8088/docs
```

## API Examples

Create and fund a testnet wallet:

```bash
curl -X POST http://127.0.0.1:8088/ripple/wallets \
  -H "Content-Type: application/json" \
  -d '{"fund": true}'
```

Create an unfunded testnet wallet:

```bash
curl -X POST http://127.0.0.1:8088/ripple/wallets \
  -H "Content-Type: application/json" \
  -d '{"fund": false}'
```

Send XRP:

```bash
curl -X POST http://127.0.0.1:8088/ripple/payments/xrp \
  -H "Content-Type: application/json" \
  -d '{
    "source_seed": "sn...",
    "destination_address": "r...",
    "amount_xrp": "1",
    "memo": "hanafi-demo-transfer"
  }'
```

Check transaction status:

```bash
curl http://127.0.0.1:8088/ripple/payments/{tx_hash}
```

## Production Notes

Before any production Ripple/XRPL usage:

- Do not return or store seeds in API responses.
- Use HSM/MPC/custody or a separate signer service.
- Add destination allowlists and transaction limits.
- Store all transactions in a database with idempotency keys.
- Wait for validated ledger results before marking settlement complete.
- Add RLUSD only after issuer, trust-line, liquidity, and compliance reviews.
