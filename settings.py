# Django settings for webme project.
from platform import node
from settings_local import *

HOSTNAME = node()

if node() == DEVELOPMENT_HOST:
    from settings_development import *
elif node() == PRODUCTION_HOST:
    from settings_production import *
else:
    raise Exception("Cannot determine execution mode for host '%s'. Please check DEVELOPMENT_HOST and PRODUCTION_HOST in settings_local.py." % node())


