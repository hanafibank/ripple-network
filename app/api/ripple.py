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
from app.services.xrpl_service import XrplService, get_xrpl_service

router = APIRouter(prefix="/ripple", tags=["Ripple / XRPL"])


@router.post("/wallets", response_model=WalletResponse)
def create_wallet(
    payload: CreateWalletRequest,
    service: XrplService = Depends(get_xrpl_service),
) -> WalletResponse:
    try:
        return service.create_wallet(fund=payload.fund)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/accounts/{address}", response_model=AccountInfoResponse)
def get_account_info(
    address: str,
    service: XrplService = Depends(get_xrpl_service),
) -> AccountInfoResponse:
    try:
        return service.get_account_info(address)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get(
    "/accounts/{address}/transactions",
    response_model=WalletTransactionHistoryResponse,
)
def get_wallet_transactions(
    address: str,
    limit: int = 20,
    service: XrplService = Depends(get_xrpl_service),
) -> WalletTransactionHistoryResponse:
    try:
        safe_limit = min(max(limit, 1), 100)
        return service.get_wallet_history(address, limit=safe_limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/payments/xrp", response_model=SendXrpResponse)
def send_xrp(
    payload: SendXrpRequest,
    service: XrplService = Depends(get_xrpl_service),
) -> SendXrpResponse:
    try:
        return service.send_xrp(payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/payments/{tx_hash}", response_model=TransactionStatusResponse)
def get_payment_status(
    tx_hash: str,
    service: XrplService = Depends(get_xrpl_service),
) -> TransactionStatusResponse:
    try:
        return service.get_transaction_status(tx_hash)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
