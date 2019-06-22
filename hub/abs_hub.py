import abc
import json
from typing import List


class AbstractHubManger(metaclass=abc.ABCMeta):

    def __init__(self, selenium_hubs: List[str]):
        self.hubs = selenium_hubs

    @classmethod
    def from_json(cls, json_config: str):
        with open(json_config, 'r') as config:
            hub_list = json.load(config)
        return cls(hub_list['selenium_hubs'])

    @abc.abstractmethod
    async def select_hub(self) -> str:
        pass

    @abc.abstractmethod
    def register_hub(self, hub_url: str) -> bool:
        pass

    @abc.abstractmethod
    def remove_hub(self, hub_url: str) -> bool:
        pass
