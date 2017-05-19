import flask.helpers

import soko.app
from soko.settings import DevConfig, ProdConfig

CONFIG = DevConfig if flask.helpers.get_debug_flag() else ProdConfig

app = soko.app.create_app(CONFIG)
