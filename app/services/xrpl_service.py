from decimal import Decimal
from functools import lru_cache
from typing import Any, Dict, Optional

from xrpl.asyncio.clients import AsyncJsonRpcClient
from xrpl.asyncio.transaction import autofill_and_sign, submit_and_wait
from xrpl.asyncio.wallet import generate_faucet_wallet
from xrpl.core.addresscodec import is_valid_classic_address
from xrpl.models.requests import AccountInfo, AccountTx, Tx
from xrpl.models.transactions import Memo, Payment
from xrpl.utils import drops_to_xrp, hex_to_str, ripple_time_to_datetime, str_to_hex, xrp_to_drops
from xrpl.wallet import Wallet

from app.core.config import Settings, get_settings
from app.schemas.ripple import (
    AccountInfoResponse,
    SendXrpRequest,
    SendXrpResponse,
    TransactionStatusResponse,
    WalletResponse,
    WalletTransactionEntry,
    WalletTransactionHistoryResponse,
)


class XrplAccountNotFoundError(Exception):
    pass


class XrplTransactionNotFoundError(Exception):
    pass


class XrplInvalidAddressError(Exception):
    pass


def _require_valid_address(address: str) -> None:
    if not is_valid_classic_address(address):
        raise XrplInvalidAddressError(f"'{address}' is not a valid XRPL classic address.")


class XrplService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = AsyncJsonRpcClient(settings.xrpl_json_rpc_url)

    async def create_wallet(self, fund: bool) -> WalletResponse:
        if fund and self.settings.xrpl_network == "mainnet":
            raise ValueError("Faucet funding is only available on testnet.")
        wallet = (
            await generate_faucet_wallet(
                self.client,
                debug=False,
                usage_context=self.settings.faucet_usage_context,
            )
            if fund
            else Wallet.create()
        )

        return WalletResponse(
            classic_address=wallet.classic_address,
            seed=wallet.seed,
            public_key=wallet.public_key,
            funded=fund,
            network=self.settings.xrpl_network,
        )

    async def get_account_info(self, address: str) -> AccountInfoResponse:
        _require_valid_address(address)
        response = await self.client.request(
            AccountInfo(
                account=address,
                ledger_index="validated",
                strict=True,
            )
        )
        if not response.is_successful():
            error = response.result.get("error")
            if error == "actNotFound":
                raise XrplAccountNotFoundError(f"Account {address} not found on {self.settings.xrpl_network}.")
            raise RuntimeError(response.result.get("error_message", "XRPL request failed."))

        result = response.result
        account_data = result.get("account_data", {})
        balance_drops = account_data.get("Balance")
        balance_xrp = Decimal(drops_to_xrp(balance_drops)) if balance_drops else None

        return AccountInfoResponse(
            address=address,
            balance_xrp=balance_xrp,
            sequence=account_data.get("Sequence"),
            ledger_index=result.get("ledger_index"),
            raw=result,
        )

    async def get_wallet_history(
        self,
        address: str,
        limit: int = 20,
        marker: Optional[Any] = None,
    ) -> WalletTransactionHistoryResponse:
        _require_valid_address(address)
        response = await self.client.request(
            AccountTx(
                account=address,
                ledger_index_min=-1,
                ledger_index_max=-1,
                binary=False,
                forward=False,
                limit=limit,
                marker=marker,
            )
        )
        if not response.is_successful():
            error = response.result.get("error")
            if error == "actNotFound":
                raise XrplAccountNotFoundError(f"Account {address} not found on {self.settings.xrpl_network}.")
            raise RuntimeError(response.result.get("error_message", "XRPL request failed."))

        result = response.result
        raw_transactions = result.get("transactions", [])
        entries = [self._build_history_entry(address, item) for item in raw_transactions]

        return WalletTransactionHistoryResponse(
            address=address,
            count=len(entries),
            limit=limit,
            next_marker=result.get("marker"),
            transactions=entries,
            raw=result,
        )

    async def send_xrp(self, payload: SendXrpRequest) -> SendXrpResponse:
        _require_valid_address(payload.destination_address)
        wallet = Wallet.from_seed(payload.source_seed)
        memo = self._build_memo(payload.memo)

        payment = Payment(
            account=wallet.classic_address,
            destination=payload.destination_address,
            amount=xrp_to_drops(payload.amount_xrp),
            memos=[memo] if memo else None,
        )

        signed_payment = await autofill_and_sign(payment, self.client, wallet)
        response = await submit_and_wait(signed_payment, self.client)
        result = response.result
        tx_hash = self._extract_hash(result)

        return SendXrpResponse(
            tx_hash=tx_hash,
            validated=bool(result.get("validated", False)),
            engine_result=self._extract_engine_result(result),
            ledger_index=self._extract_ledger_index(result),
            explorer_url=self._explorer_url(tx_hash),
            raw=result,
        )

    async def get_transaction_status(self, tx_hash: str) -> TransactionStatusResponse:
        response = await self.client.request(
            Tx(
                transaction=tx_hash,
                binary=False,
            )
        )
        if not response.is_successful():
            error = response.result.get("error")
            if error == "txnNotFound":
                raise XrplTransactionNotFoundError(f"Transaction {tx_hash} not found.")
            raise RuntimeError(response.result.get("error_message", "XRPL request failed."))

        result = response.result

        return TransactionStatusResponse(
            tx_hash=tx_hash,
            validated=bool(result.get("validated", False)),
            engine_result=self._extract_engine_result(result),
            ledger_index=self._extract_ledger_index(result),
            explorer_url=self._explorer_url(tx_hash),
            raw=result,
        )

    def _build_memo(self, memo_text: Optional[str]) -> Optional[Memo]:
        if not memo_text:
            return None

        return Memo(
            memo_data=str_to_hex(memo_text),
            memo_format=str_to_hex("text/plain"),
            memo_type=str_to_hex("hanafi-demo"),
        )

    def _extract_hash(self, result: Dict[str, Any]) -> str:
        tx_json = result.get("tx_json") or result.get("transaction") or {}
        tx_hash = result.get("hash") or tx_json.get("hash")
        if not tx_hash:
            raise ValueError("XRPL response did not include a transaction hash.")
        return tx_hash

    def _extract_engine_result(self, result: Dict[str, Any]) -> Optional[str]:
        meta = result.get("meta") or result.get("metaData") or {}
        return result.get("engine_result") or meta.get("TransactionResult")

    def _extract_ledger_index(self, result: Dict[str, Any]) -> Optional[int]:
        return result.get("ledger_index") or result.get("inLedger")

    def _explorer_url(self, tx_hash: str) -> str:
        return self.settings.xrpl_explorer_tx_url.format(tx_hash=tx_hash)

    def _build_history_entry(self, address: str, item: Dict[str, Any]) -> WalletTransactionEntry:
        tx = item.get("tx_json") or item.get("tx") or {}
        meta = item.get("meta") or item.get("metaData") or {}
        tx_hash = item.get("hash") or tx.get("hash") or ""
        account = tx.get("Account")
        destination = tx.get("Destination")
        direction = self._transaction_direction(address, account, destination)

        return WalletTransactionEntry(
            tx_hash=tx_hash,
            transaction_type=tx.get("TransactionType"),
            direction=direction,
            counterparty=self._counterparty(address, account, destination),
            amount_xrp=self._extract_xrp_amount(tx),
            fee_xrp=self._drops_to_decimal(tx.get("Fee")),
            result=meta.get("TransactionResult"),
            validated=bool(item.get("validated", False)),
            ledger_index=item.get("ledger_index") or tx.get("ledger_index"),
            date=self._format_ripple_date(tx.get("date")),
            memo=self._extract_memo(tx),
            explorer_url=self._explorer_url(tx_hash) if tx_hash else "",
        )

    def _transaction_direction(
        self,
        address: str,
        account: Optional[str],
        destination: Optional[str],
    ) -> str:
        if account == address and destination == address:
            return "self"
        if destination == address:
            return "incoming"
        if account == address:
            return "outgoing"
        return "other"

    def _counterparty(
        self,
        address: str,
        account: Optional[str],
        destination: Optional[str],
    ) -> Optional[str]:
        if account == address:
            return destination
        if destination == address:
            return account
        return account or destination

    def _extract_xrp_amount(self, tx: Dict[str, Any]) -> Optional[Decimal]:
        amount = tx.get("Amount") or tx.get("DeliverMax")
        if isinstance(amount, str):
            return self._drops_to_decimal(amount)
        return None

    def _drops_to_decimal(self, drops: Optional[str]) -> Optional[Decimal]:
        if not drops:
            return None
        return Decimal(drops_to_xrp(drops))

    def _format_ripple_date(self, value: Optional[int]) -> Optional[str]:
        if value is None:
            return None
        return ripple_time_to_datetime(value).isoformat()

    def _extract_memo(self, tx: Dict[str, Any]) -> Optional[str]:
        memos = tx.get("Memos") or []
        if not memos:
            return None
        memo_data = (memos[0].get("Memo") or {}).get("MemoData")
        if not memo_data:
            return None
        try:
            return hex_to_str(memo_data)
        except Exception:
            return memo_data


@lru_cache
def get_xrpl_service() -> XrplService:
    return XrplService(get_settings())
