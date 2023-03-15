from .config import Config

config = Config()

from .engine import Engine
from .ai import Ai


def start(*args, **kwargs):
    eng = Engine(*args, **kwargs)
    # eng.run()
    return eng
