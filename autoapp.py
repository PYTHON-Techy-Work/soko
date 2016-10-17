# -*- coding: utf-8 -*-
"""Create an application instance."""
from flask.helpers import get_debug_flag

import soko.app
from soko.settings import DevConfig, ProdConfig

CONFIG = DevConfig if get_debug_flag() else ProdConfig

app = soko.app.create_app(CONFIG)
