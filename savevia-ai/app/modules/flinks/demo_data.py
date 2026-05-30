"""Demo/sandbox account+transaction generator — port of FlinksService's
generateMock* helpers (FlinksService.java:467-584). Randomness is injected so
tests are deterministic; production passes a fresh random.Random() and uuid4.

Bug-for-bug parity note: Java writes the amount under the `"Debit"` key for BOTH
debit and credit mock transactions (line 543 and line 577), so we do the same —
the downstream amount parser treats a present `Debit` as a positive amount.
"""

from __future__ import annotations

import random
import uuid
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

# Verbatim from FlinksService.java:483-489 — (id-prefix, title, masked-number)
_CREDIT_CARD_MOCKS = [
    ("demo-cc-001", "TD Cash Back Visa Infinite", "****1234"),
    ("demo-cc-002", "TD Aeroplan Visa Infinite", "****5678"),
    ("demo-cc-003", "RBC Avion Visa Infinite", "****9012"),
    ("demo-cc-004", "Scotiabank Scene+ Visa", "****3456"),
    ("demo-cc-005", "CIBC Dividend Visa Infinite", "****7890"),
]
# Verbatim from FlinksService.java:526-535 — (description, amount)
_DEBIT_MOCKS = [
    ("INTERAC PURCHASE - LOBLAWS #1234", "178.45"),
    ("INTERAC PURCHASE - PETRO-CANADA", "72.50"),
    ("INTERAC PURCHASE - SHOPPERS DRUG MART", "38.99"),
    ("INTERAC PURCHASE - COSTCO WHOLESALE", "285.67"),
    ("INTERAC PURCHASE - SHELL", "58.00"),
    ("INTERAC PURCHASE - SOBEYS", "112.30"),
    ("INTERAC PURCHASE - REXALL PHARMA", "25.50"),
    ("INTERAC PURCHASE - ESSO", "45.00"),
]
# Verbatim from FlinksService.java:559-570 — (description, amount)
_CREDIT_MOCKS = [
    ("UBER EATS", "25.99"),
    ("NETFLIX.COM", "16.99"),
    ("TIM HORTONS", "8.45"),
    ("AMAZON.CA", "89.99"),
    ("ROGERS WIRELESS", "85.00"),
    ("STARBUCKS", "6.75"),
    ("PRESTO", "20.00"),
    ("UBER", "18.50"),
    ("BOSTON PIZZA", "52.30"),
    ("SPOTIFY", "9.99"),
]


class DemoDataGenerator:
    def __init__(
        self,
        *,
        rng: random.Random | None = None,
        uuid_factory: Callable[[], str] | None = None,
        now: Callable[[], datetime] | None = None,
    ):
        self._rng = rng or random.Random()
        self._uuid = uuid_factory or (lambda: str(uuid.uuid4()))
        self._now = now or (lambda: datetime.now(UTC))

    def _date(self) -> str:
        # Java: now.minusDays(rand.nextInt(90)).toString()
        return (self._now() - timedelta(days=self._rng.randint(0, 89))).isoformat()

    def _debit_txns(self) -> list[dict]:
        # Java generates 5-8 then iterates min(n, table_len)
        n = min(5 + self._rng.randint(0, 3), len(_DEBIT_MOCKS))
        return [
            {"Id": f"demo-debit-{self._uuid()}", "Description": d, "Debit": amt,
             "Date": self._date()}
            for d, amt in _DEBIT_MOCKS[:n]
        ]

    def _credit_txns(self) -> list[dict]:
        n = min(6 + self._rng.randint(0, 4), len(_CREDIT_MOCKS))
        return [
            {"Id": f"demo-credit-{self._uuid()}", "Description": d, "Debit": amt,
             "Date": self._date()}
            for d, amt in _CREDIT_MOCKS[:n]
        ]

    def generate_accounts_data(self) -> dict:
        accounts: list[dict] = [
            {
                "Id": f"demo-chk-{self._uuid()[:8]}",
                "Type": "Chequing",
                "Title": "Chequing Account",
                "AccountNumber": f"****{1000 + self._rng.randint(0, 8999)}",
                "Balance": str(2000 + self._rng.randint(0, 7999)),
                "Transactions": self._debit_txns(),
            }
        ]
        num_cards = 1 + self._rng.randint(0, 1)
        chosen: list[int] = []
        while len(chosen) < num_cards and len(chosen) < len(_CREDIT_CARD_MOCKS):
            idx = self._rng.randint(0, len(_CREDIT_CARD_MOCKS) - 1)
            if idx not in chosen:
                chosen.append(idx)
        for idx in chosen:
            cid, title, masked = _CREDIT_CARD_MOCKS[idx]
            accounts.append({
                "Id": f"{cid}-{self._uuid()[:8]}",
                "Type": "Credit",
                "Title": title,
                "AccountNumber": masked,
                "Balance": str(500 + self._rng.randint(0, 2999)),
                "Transactions": self._credit_txns(),
            })
        return {"Accounts": accounts}
