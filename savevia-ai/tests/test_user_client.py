import httpx
import pytest
import respx


@pytest.fixture
def user_client():
    from app.clients.user_client import UserServiceClient

    return UserServiceClient(base_url="http://user-test:8081", jwt_token="abc.def.ghi")


@respx.mock
async def test_get_user_cards_returns_parsed_json(user_client):
    route = respx.get("http://user-test:8081/api/v1/users/42/cards").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "cardName": "TD Cash"}]),
    )
    cards = await user_client.get_user_cards(user_id=42)
    assert route.called
    assert cards == [{"id": 1, "cardName": "TD Cash"}]
    assert route.calls.last.request.headers["Authorization"] == "Bearer abc.def.ghi"


@respx.mock
async def test_get_user_cards_raises_on_5xx(user_client):
    from app.clients._base import JavaServiceError

    respx.get("http://user-test:8081/api/v1/users/42/cards").mock(
        return_value=httpx.Response(503),
    )
    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_user_cards(user_id=42)
    assert exc.value.status_code == 503


@respx.mock
async def test_get_user_cards_raises_on_timeout(user_client):
    respx.get("http://user-test:8081/api/v1/users/42/cards").mock(
        side_effect=httpx.TimeoutException("timeout"),
    )
    from app.clients._base import JavaServiceError

    with pytest.raises(JavaServiceError) as exc:
        await user_client.get_user_cards(user_id=42)
    assert "timeout" in str(exc.value).lower()


@respx.mock
async def test_get_user_memory_returns_list(user_client):
    respx.get("http://user-test:8081/api/v1/memory/users/42").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "content": "likes Costco"}]),
    )
    memory = await user_client.get_user_memory(user_id=42)
    assert memory == [{"id": 1, "content": "likes Costco"}]


@respx.mock
async def test_get_chat_history_returns_list(user_client):
    respx.get(
        "http://user-test:8081/api/v1/chat/conversations/conv-1/messages"
    ).mock(return_value=httpx.Response(200, json=[{"role": "user", "content": "hi"}]))
    msgs = await user_client.get_chat_history(conversation_id="conv-1")
    assert msgs == [{"role": "user", "content": "hi"}]
