from decimal import Decimal

from fastapi.testclient import TestClient

from app.core.config import get_settings
from app.main import app
from app.services.xrpl_service import XrplService


def test_health_check():
    client = TestClient(app)

    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_history_entry_maps_xrp_payment_details():
    service = XrplService(get_settings())

    entry = service._build_history_entry(
        "rReceiver",
        {
            "hash": "ABC123",
            "ledger_index": 12345,
            "validated": True,
            "meta": {"TransactionResult": "tesSUCCESS"},
            "tx_json": {
                "Account": "rSender",
                "Destination": "rReceiver",
                "DeliverMax": "1000000",
                "Fee": "10",
                "TransactionType": "Payment",
                "date": 831266152,
                "Memos": [
                    {
                        "Memo": {
                            "MemoData": "686973746F72792D746573742D7472616E73666572"
                        }
                    }
                ],
            },
        },
    )

    assert entry.direction == "incoming"
    assert entry.counterparty == "rSender"
    assert entry.amount_xrp == Decimal("1.000000")
    assert entry.fee_xrp == Decimal("0.000010")
    assert entry.result == "tesSUCCESS"
    assert entry.memo == "history-test-transfer"
