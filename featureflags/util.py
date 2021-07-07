import logging
import sys

log = logging.getLogger(sys.modules[__name__].__name__)
log.addHandler(logging.StreamHandler())
log.setLevel(logging.DEBUG)
