from datetime import datetime
from decimal import Decimal


def test_bank_connection_dto_camelcase_and_datetime_format():
    from app.modules.bank.schema import BankAccountDTO, BankConnectionDTO

    dto = BankConnectionDTO(
        id=7,
        institution_name="TD Canada Trust",
        status="CONNECTED",
        last_sync_at=datetime(2026, 5, 30, 9, 8, 7),
        error_message=None,
        created_at=datetime(2026, 5, 1, 0, 0, 0),
        accounts=[
            BankAccountDTO(
                id=11, account_type="CREDIT_CARD", account_name="TD Cash Back Visa",
                account_number_masked="****1234", balance=Decimal("1234.50"),
                is_active=True,
            )
        ],
    )
    data = dto.model_dump(by_alias=True, mode="json")
    assert data["institutionName"] == "TD Canada Trust"
    assert data["lastSyncAt"] == "2026-05-30T09:08:07"   # no millis, no tz
    assert data["createdAt"] == "2026-05-01T00:00:00"
    acct = data["accounts"][0]
    assert acct["accountNumberMasked"] == "****1234"
    assert acct["isActive"] is True
    assert acct["balance"] == 1234.5                      # JSON number, not string


def test_flinks_connect_request_parses_camelcase_body():
    from app.modules.bank.schema import FlinksConnectRequest

    req = FlinksConnectRequest.model_validate(
        {"loginId": "demo-abc", "institutionName": "TD", "userCardIds": [1, 2]}
    )
    assert req.login_id == "demo-abc"
    assert req.user_card_ids == [1, 2]
