from server.server import WebApp
from hub.hub_managers import RoundRobinManager


if __name__ == '__main__':
    WebApp('0.0.0.0', 8002).run('./configs.json')