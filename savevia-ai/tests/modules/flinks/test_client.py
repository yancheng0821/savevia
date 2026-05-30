import httpx
import respx


@respx.mock
async def test_authorize_posts_loginid_and_returns_request_id():
    from app.modules.flinks.client import FlinksClient

    base = "https://flinks.test/v3"
    cust = "cust-1"
    route = respx.post(f"{base}/{cust}/BankingServices/Authorize").mock(
        return_value=httpx.Response(200, json={"RequestId": "req-123"})
    )
    client = FlinksClient(base_url=base, customer_id=cust)
    rid = await client.authorize("login-xyz")
    assert rid == "req-123"
    assert route.called
    sent = route.calls.last.request
    assert b"login-xyz" in sent.content
    await client.aclose()


@respx.mock
async def test_get_accounts_detail_returns_accounts_payload():
    from app.modules.flinks.client import FlinksClient

    base = "https://flinks.test/v3"
    cust = "cust-1"
    respx.post(f"{base}/{cust}/BankingServices/GetAccountsDetail").mock(
        return_value=httpx.Response(200, json={"Accounts": [{"Id": "a1"}]})
    )
    client = FlinksClient(base_url=base, customer_id=cust)
    data = await client.get_accounts_detail("req-123", max_retries=1, sleep_seconds=0)
    assert data["Accounts"][0]["Id"] == "a1"
    await client.aclose()
