import datetime as dt
import json
import os

from forwarder import Forwarder

from aiohttp.web import Request
from aiohttp import web, ClientTimeout


SELENIUM_TIMEOUT = ClientTimeout(total=int(os.getenv('SELENIUM_TIMEOUT', 300)))


def error_on_timeout():
    return web.json_response(data={
        "value": {
            "error": "timeout",
            "message": "Exceeded set timeout",
            "stacktrace": ""
        }
    }, status=500)


def get_server_location(request: Request):
    session_id = request.match_info['session_id']
    server_string, _ = request.app['session_cache'].get(session_id)
    request.app['session_cache'][session_id] = (server_string, dt.datetime.now())
    return '{}{}'.format(server_string.rstrip('/'), request.raw_path)


async def handle_get(request: Request):
    url = get_server_location(request)
    try:
        f = Forwarder(url, 'GET', None, request.headers)
        resp, req = await f.forward(SELENIUM_TIMEOUT)
    except ClientTimeout:
        return error_on_timeout()
    return web.json_response(resp, status=req.status)


async def handle_post(request: Request):
    payload = await request.json()
    url = get_server_location(request)
    try:
        f = Forwarder(url, 'POST', payload, request.headers)
        resp, req = await f.forward(SELENIUM_TIMEOUT)
    except ClientTimeout:
        return error_on_timeout()
    return web.json_response(resp, status=req.status)


async def handle_delete(request: Request):
    url = get_server_location(request)
    f = Forwarder(url, 'DELETE', None, request.headers)
    resp, req = await f.forward(SELENIUM_TIMEOUT)
    return web.json_response(resp, status=req.status)


async def new_session(request):
    """
    POST /session creates a new session
    :param request:
    :return:
    """
    hub = await request.app['selenium_hubs'].select_hub()
    payload = await request.json()
    url = '{}/session'.format(hub.rstrip('/'))
    f = Forwarder(url, 'POST', payload, request.headers)
    try:
        resp, req = await f.forward(SELENIUM_TIMEOUT)
    except ClientTimeout:
        return error_on_timeout()
    if 'sessionId' in resp:
        sess_id = resp['sessionId']
        request.app['session_cache'][sess_id] = (hub, dt.datetime.now())
    return web.json_response(resp, status=req.status)


async def delete_session(request: Request):
    """
    DELETE /session/{session_id}
    :param request:
    :return:
    """
    session_id = request.match_info['session_id']
    url = get_server_location(request)
    f = Forwarder(url, 'DELETE', None, request.headers)
    try:
        resp, req = await f.forward(SELENIUM_TIMEOUT)
    except ClientTimeout:
        return error_on_timeout()
    if session_id in request.app['session_cache']:
        request.app['session_cache'].pop(session_id)
    return web.json_response(resp)


def add_session_routes(app: web.Application) -> web.Application:
    handlers = {'handle_get': handle_get, 'handle_post': handle_post, 'handle_delete': handle_delete}
    with open('route_config.json', 'r') as json_config:
        configs = json.load(json_config)
    routes = []
    for item in configs:
        routes.append(web.route(item['method'], item['route'], handlers[item['handler']]))
    app.add_routes(routes)
    return app
