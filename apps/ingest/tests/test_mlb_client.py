import pytest

from apps.ingest.app.mlb_client import MLBApiClient, MLBResponse


class FakeRequester:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def __call__(self, url: str, timeout: int) -> MLBResponse:
        self.calls.append((url, timeout))
        return self._responses.pop(0)


def test_get_json_retries_on_429_then_succeeds():
    requester = FakeRequester(
        [
            MLBResponse(429, {"message": "slow down"}, headers={"Retry-After": "0"}),
            MLBResponse(200, {"dates": []}, headers={}),
        ]
    )
    sleeps = []

    client = MLBApiClient(base_url="http://mock:8090", request_fn=requester, sleep_fn=sleeps.append)
    response = client.get_json("/api/v1/schedule")

    assert isinstance(response, MLBResponse)
    assert response.status_code == 200
    assert response.payload == {"dates": []}
    assert len(requester.calls) == 2
    assert sleeps == [0.0]


def test_get_json_raises_after_exhausted_retries():
    requester = FakeRequester([
        MLBResponse(429, {}, headers={}),
        MLBResponse(429, {}, headers={}),
        MLBResponse(429, {}, headers={}),
    ])
    client = MLBApiClient(base_url="http://mock:8090", request_fn=requester, max_retries=2, sleep_fn=lambda _: None)

    with pytest.raises(RuntimeError, match="MLB API request failed"):
        client.get_json("/api/v1/schedule")
