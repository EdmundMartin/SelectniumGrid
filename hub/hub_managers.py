import asyncio
import os
from random import choice
from typing import Dict, List, Union
from urllib.parse import urlparse


import aiohttp

from hub.abs_hub import AbstractHubManger


DEFAULT_CLIENT_TIMEOUT = aiohttp.ClientTimeout(total=int(os.getenv('CLIENT_TIMEOUT', 10)))


class RandomHubManager(AbstractHubManger):

    def __init__(self, selenium_hubs: List[str]):
        super().__init__(selenium_hubs)

    async def select_hub(self):
        return choice(self.hubs)

    def register_hub(self, hub_url: str) -> bool:
        if hub_url not in self.hubs:
            self.hubs.append(hub_url)
            return True
        return False

    def remove_hub(self, hub_url: str) -> bool:
        if hub_url in self.hubs:
            self.hubs.remove(hub_url)
            return True
        return False


class RoundRobinManager(AbstractHubManger):

    def __init__(self, hubs: List[str]):
        super().__init__(hubs)
        self.idx = 0

    async def select_hub(self) -> str:
        hub = self.hubs[self.idx % len(self.hubs)]
        self.idx += 1
        return hub

    def register_hub(self, hub_url: str) -> bool:
        if hub_url not in self.hubs:
            self.hubs.append(hub_url)
            return True
        return False

    def remove_hub(self, hub_url: str) -> bool:
        if hub_url in self.hubs:
            self.hubs.remove(hub_url)
            return True
        return False


def hub_api_url(hub_url: str):
    parsed = urlparse(hub_url)
    return '{}://{}/grid/api/hub'.format(parsed.scheme, parsed.netloc)


async def get_hub_status(hub_url: str) -> Union[Dict, None]:
    hub_api = hub_api_url(hub_url)
    async with aiohttp.ClientSession(timeout=DEFAULT_CLIENT_TIMEOUT) as session:
        try:
            resp = await session.get(hub_api)
            if resp.status == 200:
                json_load = await resp.json()
                return {'hub': hub_url, 'free_nodes': json_load['slotCounts']['free'],
                        'queue_size': json_load['newSessionRequestCount']}
        except aiohttp.ClientError:
            return


class ApiManager(AbstractHubManger):

    def __init__(self, hubs: List[str]):
        super().__init__(hubs)

    async def select_hub(self):
        requests = [
            get_hub_status(url) for url in self.hubs
        ]
        results = []
        for next_to_complete in asyncio.as_completed(requests):
            result = await next_to_complete
            if result and result['free_nodes'] > 0:
                return result['hub']
            elif result:
                results.append(result)
        if results:
            sorted_hub = sorted(results, key=lambda k: k['queue_size'])
            return sorted_hub[0]['hub']
        return choice(self.hubs)

    def register_hub(self, hub_url: str):
        if hub_url not in self.hubs:
            self.hubs.append(hub_url)
            return True
        return False

    def remove_hub(self, hub_url: str):
        if hub_url in self.hubs:
            self.hubs.remove(hub_url)
            return True
        return False
