import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class Settings:
    app_name: str = "HanaFi Ripple Engine Prototype"
    xrpl_json_rpc_url: str = os.getenv(
        "XRPL_JSON_RPC_URL",
        "https://s.altnet.rippletest.net:51234/",
    )
    xrpl_explorer_tx_url: str = os.getenv(
        "XRPL_EXPLORER_TX_URL",
        "https://testnet.xrpl.org/transactions/{tx_hash}",
    )
    faucet_usage_context: str = os.getenv(
        "FAUCET_USAGE_CONTEXT",
        "hanafi-ripple-engine-demo",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

