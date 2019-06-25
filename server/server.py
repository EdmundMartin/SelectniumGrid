import asyncio
import datetime as dt
import os
from typing import Any, Dict, Union

from aiohttp import web


from server.routes import new_session, delete_session, add_session_routes


async def clean_dead_sessions(cache):
    while True:
        for k, v in cache.items():
            _, created = v
            if dt.datetime.now() - dt.timedelta(seconds=600) > created:
                cache.pop(k)
            await asyncio.sleep(0.5)
        await asyncio.sleep(5)


def import_hub_manager(hub_klass: str):
    components = hub_klass.split('.')
    mod = __import__(components[0])
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


class WebApp:

    def __init__(self, host: str, port: int, loop: Union[None, asyncio.AbstractEventLoop]=None) -> None:
        self.host = host
        self.port = port
        self.loop = loop if loop else asyncio.get_event_loop()

    async def create_app(self, configs: str):
        app = web.Application()
        hub_manager = import_hub_manager(os.getenv('HUB_MANAGER_CLASS', 'hub.ApiManager'))
        app['selenium_hubs'] = hub_manager.from_json(configs)
        app['session_cache']: Dict[str, Any] = {}
        app.add_routes([
            web.route('POST', '/session', new_session),
            web.route('DELETE', '/session/{session_id}', delete_session)
        ])
        loop = asyncio.get_event_loop()
        app['clean_sessions'] = loop.create_task(clean_dead_sessions(app['session_cache']))
        app = add_session_routes(app)
        return app

    def run(self, configs: str):
        loop = self.loop
        app = loop.run_until_complete(self.create_app(configs))
        web.run_app(app, host=self.host, port=self.port)
