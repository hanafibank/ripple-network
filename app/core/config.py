import os
from dataclasses import dataclass
from functools import lru_cache

_NETWORK_DEFAULTS = {
    "mainnet": {
        "rpc_url": "https://xrplcluster.com/",
        "explorer_tx_url": "https://livenet.xrpl.org/transactions/{tx_hash}",
    },
    "testnet": {
        "rpc_url": "https://s.altnet.rippletest.net:51234/",
        "explorer_tx_url": "https://testnet.xrpl.org/transactions/{tx_hash}",
    },
}


@dataclass(frozen=True)
class Settings:
    app_name: str
    xrpl_network: str
    xrpl_json_rpc_url: str
    xrpl_explorer_tx_url: str
    faucet_usage_context: str


@lru_cache
def get_settings() -> Settings:
    network = os.getenv("XRPL_NETWORK", "testnet").lower()
    defaults = _NETWORK_DEFAULTS.get(network, _NETWORK_DEFAULTS["testnet"])

    return Settings(
        app_name="HanaFi Ripple Engine Prototype",
        xrpl_network=network,
        xrpl_json_rpc_url=os.getenv("XRPL_JSON_RPC_URL", defaults["rpc_url"]),
        xrpl_explorer_tx_url=os.getenv("XRPL_EXPLORER_TX_URL", defaults["explorer_tx_url"]),
        faucet_usage_context=os.getenv("FAUCET_USAGE_CONTEXT", "hanafi-ripple-engine-demo"),
    )
