def test_signatures_exist():
    from app.repositories.connection_limit_repository import ConnectionLimitRepository

    for m in ("find_by_user_and_month", "insert", "update_connection_count",
              "insert_history"):
        assert hasattr(ConnectionLimitRepository, m)
