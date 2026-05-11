import json
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException

from app.schemas.ripple import (
    AccountInfoResponse,
    CreateWalletRequest,
    SendXrpRequest,
    SendXrpResponse,
    TransactionStatusResponse,
    WalletResponse,
    WalletTransactionHistoryResponse,
)
from app.services.xrpl_service import (
    XrplAccountNotFoundError,
    XrplInvalidAddressError,
    XrplService,
    XrplTransactionNotFoundError,
    get_xrpl_service,
)

router = APIRouter(prefix="/ripple", tags=["Ripple / XRPL"])


def _parse_marker(marker: Optional[str]) -> Optional[Any]:
    if not marker:
        return None
    try:
        return json.loads(marker)
    except (json.JSONDecodeError, TypeError):
        return marker


@router.post("/wallets", response_model=WalletResponse)
async def create_wallet(
    payload: CreateWalletRequest,
    service: XrplService = Depends(get_xrpl_service),
) -> WalletResponse:
    try:
        return await service.create_wallet(fund=payload.fund)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/accounts/{address}", response_model=AccountInfoResponse)
async def get_account_info(
    address: str,
    service: XrplService = Depends(get_xrpl_service),
) -> AccountInfoResponse:
    try:
        return await service.get_account_info(address)
    except XrplInvalidAddressError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except XrplAccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/accounts/{address}/transactions",
    response_model=WalletTransactionHistoryResponse,
)
async def get_wallet_transactions(
    address: str,
    limit: int = 20,
    marker: Optional[str] = None,
    service: XrplService = Depends(get_xrpl_service),
) -> WalletTransactionHistoryResponse:
    try:
        safe_limit = min(max(limit, 1), 100)
        return await service.get_wallet_history(
            address,
            limit=safe_limit,
            marker=_parse_marker(marker),
        )
    except XrplInvalidAddressError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except XrplAccountNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/payments/xrp", response_model=SendXrpResponse)
async def send_xrp(
    payload: SendXrpRequest,
    service: XrplService = Depends(get_xrpl_service),
) -> SendXrpResponse:
    try:
        return await service.send_xrp(payload)
    except XrplInvalidAddressError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/payments/{tx_hash}", response_model=TransactionStatusResponse)
async def get_payment_status(
    tx_hash: str,
    service: XrplService = Depends(get_xrpl_service),
) -> TransactionStatusResponse:
    try:
        return await service.get_transaction_status(tx_hash)
    except XrplTransactionNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
