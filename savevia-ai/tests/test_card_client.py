import httpx
import pytest
import respx


@pytest.fixture
def card_client():
    from app.clients.card_client import CardServiceClient

    return CardServiceClient(base_url="http://card-test:8082", jwt_token="abc.def.ghi")


@respx.mock
async def test_search_cards(card_client):
    respx.get("http://card-test:8082/api/v1/cards/search").mock(
        return_value=httpx.Response(
            200, json=[{"id": 1, "cardName": "Costco Mastercard"}]
        ),
    )
    cards = await card_client.search_cards(query="costco", category=None)
    assert cards[0]["cardName"] == "Costco Mastercard"


@respx.mock
async def test_get_cards_batch(card_client):
    route = respx.post("http://card-test:8082/api/v1/cards/batch").mock(
        return_value=httpx.Response(
            200, json=[{"id": 1}, {"id": 2}, {"id": 3}]
        ),
    )
    cards = await card_client.get_cards_batch(card_ids=[1, 2, 3])
    assert route.called
    assert len(cards) == 3
    assert route.calls.last.request.read() == b'{"ids":[1,2,3]}'


@respx.mock
async def test_get_card_usage_tips(card_client):
    respx.get("http://card-test:8082/api/v1/cards/5/usage-tips").mock(
        return_value=httpx.Response(200, json=[{"tip": "Use at gas stations"}]),
    )
    tips = await card_client.get_card_usage_tips(card_id=5)
    assert tips[0]["tip"] == "Use at gas stations"
