import random
from datetime import datetime


def _factory(seed: int = 7):
    from app.modules.flinks.demo_data import DemoDataGenerator
    rng = random.Random(seed)
    counter = {"n": 0}

    def fake_uuid() -> str:
        counter["n"] += 1
        return f"uuid{counter['n']:04d}"

    return DemoDataGenerator(rng=rng, uuid_factory=fake_uuid,
                             now=lambda: datetime(2026, 5, 30, 12, 0, 0))


def test_generate_accounts_is_deterministic_with_seed():
    a = _factory(7).generate_accounts_data()
    b = _factory(7).generate_accounts_data()
    assert a == b  # same seed → identical structure


def test_generate_accounts_has_one_chequing_plus_credit_cards():
    data = _factory(7).generate_accounts_data()
    accounts = data["Accounts"]
    types = [acc["Type"] for acc in accounts]
    assert types[0] == "Chequing"               # always first
    assert any(t == "Credit" for t in types)    # 1-2 credit cards
    assert 2 <= len(accounts) <= 3
    for acc in accounts:
        for txn in acc["Transactions"]:
            assert {"Id", "Description", "Debit", "Date"} <= set(txn)
