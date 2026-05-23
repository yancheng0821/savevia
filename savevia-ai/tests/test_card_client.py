"""Tests for CardServiceClient.

Card endpoints are public — no X-User-Id required.
All responses are Java `Result<T>` envelopes; client unwraps to `data`.
"""
import httpx
import pytest
import respx

CARD_BASE = "http://card-test:8082"


def _result(data, code: int = 200, message: str = "success") -> dict:
    return {"code": code, "message": message, "data": data, "timestamp": 1234567890}


@pytest.fixture
def card_client():
    from app.clients.card_client import CardServiceClient

    return CardServiceClient(base_url=CARD_BASE)


@respx.mock
async def test_list_all_cards_unwraps_envelope(card_client):
    respx.get(f"{CARD_BASE}/api/v1/cards").mock(
        return_value=httpx.Response(
            200, json=_result([{"id": 1, "cardName": "TD Cash"}])
        ),
    )
    cards = await card_client.list_all_cards()
    assert cards == [{"id": 1, "cardName": "TD Cash"}]


@respx.mock
async def test_get_card_returns_single_dto(card_client):
    respx.get(f"{CARD_BASE}/api/v1/cards/5").mock(
        return_value=httpx.Response(200, json=_result({"id": 5, "cardName": "Costco"})),
    )
    card = await card_client.get_card(card_id=5)
    assert card["cardName"] == "Costco"


@respx.mock
async def test_get_cards_batch_sends_raw_list(card_client):
    """POST body must be a raw JSON array `[1,2,3]`, not `{"ids":[...]}`.

    Java endpoint: `getCardsByIds(@RequestBody List<Long> ids)`
    """
    route = respx.post(f"{CARD_BASE}/api/v1/cards/batch").mock(
        return_value=httpx.Response(
            200, json=_result([{"id": 1}, {"id": 2}, {"id": 3}])
        ),
    )
    cards = await card_client.get_cards_batch(card_ids=[1, 2, 3])
    assert len(cards) == 3
    assert route.calls.last.request.read() == b"[1,2,3]"


@respx.mock
async def test_get_card_usage_guide_returns_single_dto(card_client):
    """Java returns Result<CardUsageGuideDTO> — singular object, not list."""
    route = respx.get(f"{CARD_BASE}/api/v1/cards/5/usage-guide").mock(
        return_value=httpx.Response(
            200,
            json=_result(
                {
                    "cardId": 5,
                    "lang": "en",
                    "tips": [{"category": "gas", "tip": "Use at gas stations"}],
                }
            ),
        ),
    )
    guide = await card_client.get_card_usage_guide(card_id=5, lang="en")
    assert guide["cardId"] == 5
    assert guide["tips"][0]["category"] == "gas"
    # Default lang param is passed
    assert route.calls.last.request.url.params["lang"] == "en"


@respx.mock
async def test_get_cards_by_bank(card_client):
    respx.get(f"{CARD_BASE}/api/v1/cards/bank/TD").mock(
        return_value=httpx.Response(200, json=_result([{"id": 1, "bank": "TD"}])),
    )
    cards = await card_client.get_cards_by_bank("TD")
    assert cards[0]["bank"] == "TD"


@respx.mock
async def test_post_does_not_retry_on_5xx(card_client):
    """POST is not idempotent — must NOT retry on 5xx."""
    from app.clients._base import JavaServiceError

    route = respx.post(f"{CARD_BASE}/api/v1/cards/batch").mock(
        return_value=httpx.Response(503),
    )
    with pytest.raises(JavaServiceError) as exc:
        await card_client.get_cards_batch(card_ids=[1])
    assert exc.value.status_code == 503
    assert route.call_count == 1  # NO retry


@respx.mock
async def test_get_retries_on_5xx_then_succeeds(card_client):
    route = respx.get(f"{CARD_BASE}/api/v1/cards").mock(
        side_effect=[
            httpx.Response(503),
            httpx.Response(200, json=_result([{"id": 1}])),
        ],
    )
    cards = await card_client.list_all_cards()
    assert cards == [{"id": 1}]
    assert route.call_count == 2


@respx.mock
async def test_business_error_on_get(card_client):
    """HTTP 200 + non-200 envelope code raises JavaServiceError."""
    from app.clients._base import JavaServiceError

    respx.get(f"{CARD_BASE}/api/v1/cards/999").mock(
        return_value=httpx.Response(
            200, json=_result(None, code=404, message="card not found")
        ),
    )
    with pytest.raises(JavaServiceError) as exc:
        await card_client.get_card(card_id=999)
    assert exc.value.status_code == 404
    assert "not found" in exc.value.message


@respx.mock
async def test_no_x_user_id_sent_on_card_calls(card_client):
    """Card endpoints are public; we must not send X-User-Id when we don't have one."""
    route = respx.get(f"{CARD_BASE}/api/v1/cards/1").mock(
        return_value=httpx.Response(200, json=_result({"id": 1})),
    )
    await card_client.get_card(card_id=1)
    assert "X-User-Id" not in route.calls.last.request.headers


@respx.mock
async def test_aclose_releases_client(card_client):
    respx.get(f"{CARD_BASE}/api/v1/cards").mock(
        return_value=httpx.Response(200, json=_result([])),
    )
    await card_client.list_all_cards()
    assert card_client._client is not None and not card_client._client.is_closed
    await card_client.aclose()
    assert card_client._client.is_closed
