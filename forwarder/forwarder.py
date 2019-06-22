from typing import Dict, Tuple, Union

from aiohttp.client import ClientSession, ClientResponse, ClientTimeout


class Forwarder:

    def __init__(self, location: str, method: str, payload: Union[Dict, None], headers):
        self.location = location
        self.method = method
        self.payload = payload
        self.headers = headers

    async def forward(self, timeout: ClientTimeout) -> Tuple[Dict, ClientResponse]:
        async with ClientSession(headers=self.headers, timeout=timeout) as client:
            response = await client._request(self.method, self.location, json=self.payload)
            json_resp = await response.json()
        return json_resp, response
