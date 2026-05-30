def test_signatures_exist():
    from app.repositories.bank_connection_repository import BankConnectionRepository

    for m in ("find_by_user_id", "find_by_id", "find_by_user_and_login_id",
              "find_by_user_and_institution", "insert", "update_status"):
        assert hasattr(BankConnectionRepository, m)
