from decimal import Decimal
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CreateWalletRequest(BaseModel):
    fund: bool = Field(
        default=True,
        description="When true, fund the wallet using the XRPL testnet faucet.",
    )


class WalletResponse(BaseModel):
    classic_address: str
    seed: str
    public_key: str
    funded: bool
    network: str = "testnet"
    warning: str = (
        "Demo only. Never expose or store wallet seeds like this in production."
    )


class AccountInfoResponse(BaseModel):
    address: str
    balance_xrp: Optional[Decimal] = None
    sequence: Optional[int] = None
    ledger_index: Optional[int] = None
    raw: Dict[str, Any]


class SendXrpRequest(BaseModel):
    source_seed: str = Field(
        min_length=20,
        description="XRPL testnet wallet seed for the sender.",
    )
    destination_address: str = Field(
        min_length=25,
        description="XRPL classic address for the recipient.",
    )
    amount_xrp: Decimal = Field(
        gt=Decimal("0"),
        description="Amount of XRP to send.",
    )
    memo: Optional[str] = Field(
        default=None,
        max_length=256,
        description="Optional non-sensitive memo for demo reconciliation.",
    )


class SendXrpResponse(BaseModel):
    tx_hash: str
    validated: bool
    engine_result: Optional[str] = None
    ledger_index: Optional[int] = None
    explorer_url: str
    raw: Dict[str, Any]


class TransactionStatusResponse(BaseModel):
    tx_hash: str
    validated: bool
    engine_result: Optional[str] = None
    ledger_index: Optional[int] = None
    explorer_url: str
    raw: Dict[str, Any]

