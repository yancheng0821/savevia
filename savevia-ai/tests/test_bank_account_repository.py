def test_signatures_exist():
    from app.repositories.bank_account_repository import BankAccountRepository

    for m in ("find_by_connection_id", "insert", "update"):
        assert hasattr(BankAccountRepository, m)
