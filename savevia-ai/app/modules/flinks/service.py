"""FlinksService — Python port of com.savevia.optimizer.service.FlinksService.

Demo/sandbox is the live path (no Flinks contract); the real REST client is
inert and reached only when sandbox=False and loginId is not a demo id.
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from app.core.logging import get_logger
from app.models.bank_account import BankAccount
from app.models.bank_connection import BankConnection
from app.models.transaction import Transaction

if TYPE_CHECKING:
    from app.modules.bank.schema import FlinksConnectRequest

_log = get_logger("savevia-ai.flinks")


class FlinksService:
    def __init__(
        self,
        *,
        bank_connection_repo,
        bank_account_repo,
        transaction_repo,
        categorization,
        card_client,
        connection_limits,
        demo_factory: Callable[[], Any],
        flinks_client_factory: Callable[[], Any],
        sandbox: bool,
    ):
        self._conn_repo = bank_connection_repo
        self._acct_repo = bank_account_repo
        self._txn_repo = transaction_repo
        self._cat = categorization
        self._card = card_client
        self._limits = connection_limits
        self._demo_factory = demo_factory
        self._flinks_client_factory = flinks_client_factory
        self._sandbox = sandbox

    # ---- public lifecycle ------------------------------------------------

    async def connect_bank(
        self, user_id: int, request: "FlinksConnectRequest"
    ) -> BankConnection:
        existing = await self._conn_repo.find_by_user_and_login_id(
            user_id, request.login_id
        )
        if existing is not None:
            existing.status = "REFRESHING"
            await self._conn_repo.update_status(existing)
            await self.refresh_bank_data(existing)
            await self._limits.record_refresh(
                user_id, existing.institution_name, existing.flinks_login_id
            )
            return existing

        by_inst = await self._conn_repo.find_by_user_and_institution(
            user_id, request.institution_name
        )
        if by_inst is not None:
            by_inst.status = "REFRESHING"
            by_inst.flinks_login_id = request.login_id
            await self._conn_repo.update_status(by_inst)
            await self.refresh_bank_data(by_inst)
            await self._limits.record_refresh(
                user_id, by_inst.institution_name, by_inst.flinks_login_id
            )
            return by_inst

        if not await self._limits.can_connect(user_id):
            remaining = await self._limits.get_remaining_connections(user_id)
            _log.warning("connect_limit_reached", user_id=user_id, remaining=remaining)
            raise RuntimeError(
                "LIMIT_EXCEEDED:You have reached your monthly bank connection limit "
                "(5 per month). Please try again next month."
            )

        connection = BankConnection(
            user_id=user_id,
            flinks_login_id=request.login_id,
            institution_name=request.institution_name,
            status="PENDING",
        )
        await self._conn_repo.insert(connection)
        try:
            await self._fetch_flinks_data(connection, request.user_card_ids)
            connection.status = "CONNECTED"
            connection.last_sync_at = datetime.now(timezone.utc).replace(tzinfo=None)
            await self._limits.record_connection(
                user_id, request.institution_name, request.login_id
            )
        except Exception as e:  # noqa: BLE001 — mirror Java: failed fetch → ERROR
            _log.error("flinks_fetch_failed", error=str(e))
            connection.status = "ERROR"
            connection.error_message = str(e)
        await self._conn_repo.update_status(connection)
        return connection

    async def refresh_bank_data(self, connection: BankConnection) -> None:
        # Local-only: no Flinks API call, and DO NOT update last_sync_at.
        connection.status = "CONNECTED"
        connection.error_message = None
        await self._conn_repo.update_status(connection)

    async def force_refresh_bank_data(
        self, connection: BankConnection, user_card_ids: list[int] | None
    ) -> None:
        try:
            await self._fetch_flinks_data(connection, user_card_ids)
            connection.status = "CONNECTED"
            connection.last_sync_at = datetime.now(timezone.utc).replace(tzinfo=None)
            connection.error_message = None
        except Exception as e:  # noqa: BLE001
            _log.error("flinks_force_refresh_failed", error=str(e))
            connection.status = "ERROR"
            connection.error_message = str(e)
        await self._conn_repo.update_status(connection)

    # ---- fetch + persist -------------------------------------------------

    async def _authorize(self, login_id: str) -> str:
        if self._sandbox or login_id.startswith("demo-"):
            return f"demo-request-{uuid.uuid4()}"
        return await self._flinks_client_factory().authorize(login_id)

    async def _get_accounts_detail(self, request_id: str) -> dict:
        if request_id.startswith("demo-"):
            return self._demo_factory().generate_accounts_data()
        return await self._flinks_client_factory().get_accounts_detail(request_id)

    async def _fetch_flinks_data(
        self, connection: BankConnection, user_card_ids: list[int] | None
    ) -> None:
        user_cards: list[dict] = []
        if user_card_ids:
            try:
                user_cards = await self._card.get_cards_batch(user_card_ids) or []
            except Exception as e:  # noqa: BLE001
                _log.warning("fetch_user_cards_failed", error=str(e))
        request_id = await self._authorize(connection.flinks_login_id)
        data = await self._get_accounts_detail(request_id)
        for account_data in data.get("Accounts", []) or []:
            await self._save_or_update_account(connection, account_data, user_cards)

    async def _save_or_update_account(
        self, connection, account_data, user_cards
    ) -> None:
        flinks_account_id = account_data.get("Id")
        account_type = self._map_account_type(account_data.get("Type"))
        account_name = account_data.get("Title")

        existing = await self._acct_repo.find_by_connection_id(connection.id)
        account = next(
            (a for a in existing if a.flinks_account_id == flinks_account_id), None
        )

        linked_card_id = None
        if account_type == "CREDIT_CARD" and user_cards:
            linked_card_id = self._match_credit_card_to_user_card(
                account_name, connection.institution_name, user_cards
            )

        if account is None:
            account = BankAccount(
                connection_id=connection.id,
                user_id=connection.user_id,
                flinks_account_id=flinks_account_id,
                account_type=account_type,
                account_name=account_name,
                account_number_masked=self._mask_account_number(
                    account_data.get("AccountNumber")
                ),
                institution_name=connection.institution_name,
                is_active=True,
                linked_card_id=linked_card_id,
            )
            await self._acct_repo.insert(account)
        elif linked_card_id is not None and account.linked_card_id is None:
            account.linked_card_id = linked_card_id

        balance = account_data.get("Balance")
        if balance is not None:
            account.balance = Decimal(str(balance))
            await self._acct_repo.update(account)

        await self._save_transactions(account, account_data.get("Transactions") or [])

    async def _save_transactions(self, account, transactions_data) -> None:
        for txn_data in transactions_data:
            flinks_id = txn_data.get("Id")
            existing = await self._txn_repo.find_by_account_and_flinks_id(
                account.id, flinks_id
            )
            if existing:
                continue
            debit = txn_data.get("Debit")
            credit = txn_data.get("Credit")
            amount = (
                Decimal(str(debit)) if debit is not None
                else Decimal("-" + str(credit))
            )
            merchant = txn_data.get("Description")
            date_str = txn_data.get("Date")
            txn = Transaction(
                user_id=account.user_id,
                account_id=account.id,
                flinks_transaction_id=flinks_id,
                amount=amount,
                merchant=merchant,
                description=merchant,
                transaction_date=(
                    datetime.fromisoformat(date_str[:19]) if date_str else None
                ),
                category=self._cat.categorize(merchant),
                is_analyzed=False,
            )
            if account.account_type == "CREDIT_CARD" and account.linked_card_id is not None:
                txn.card_used_id = account.linked_card_id
            await self._txn_repo.insert(txn)

    # ---- helpers (verbatim ports) ---------------------------------------

    def _match_credit_card_to_user_card(
        self, account_name, institution_name, user_cards
    ):
        # Verbatim port of FlinksService.java:348-393
        if not account_name or not institution_name:
            return None
        norm_name = account_name.upper()
        bank_short = institution_name.upper().split(" ")[0]
        best_match = None
        best_score = 0
        for card in user_cards:
            bank = (card.get("bank") or "").upper()
            if bank_short not in bank and bank not in bank_short:
                continue
            score = 0
            for kw in (card.get("name") or "").upper().split(" "):
                if len(kw) >= 3 and kw in norm_name:
                    score += len(kw)
            for hint, need in (
                ("VISA", "VISA"), ("MASTERCARD", "MASTERCARD"), ("AMEX", "AMEX"),
                ("CASHBACK", "CASH"), ("INFINITE", "INFINITE"),
            ):
                if hint in norm_name and need in (card.get("name") or "").upper():
                    score += 5
            if score > best_score:
                best_score = score
                best_match = card
        return best_match.get("id") if best_score >= 3 and best_match else None

    @staticmethod
    def _map_account_type(flinks_type: str | None) -> str:
        if not flinks_type:
            return "OTHER"
        return {
            "CHEQUING": "CHECKING", "CHECKING": "CHECKING", "SAVINGS": "SAVINGS",
            "CREDIT": "CREDIT_CARD", "CREDITCARD": "CREDIT_CARD",
            "LOC": "LINE_OF_CREDIT", "LINEOFCREDIT": "LINE_OF_CREDIT",
        }.get(flinks_type.upper(), "OTHER")

    @staticmethod
    def _mask_account_number(account_number: str | None) -> str:
        if not account_number or len(account_number) < 4:
            return "****"
        return "****" + account_number[-4:]
