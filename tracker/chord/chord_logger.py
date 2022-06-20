import logging

'''Logging for chord nodes connection'''

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%{asctime}s [%(levelname)s] %(message)s", datefmt="%H:%M:%S"))
logger.addHandler(handler)
