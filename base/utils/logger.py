import sys

from loguru import logger

fmt = "<green>{level} {time:YYYY-MM-DD HH:mm:ss.SSS}</green> | {line}:{function} | {message}"

logger.remove()
logger.add(sys.stdout, colorize=True, format=fmt, backtrace=True, diagnose=True)

plog = logger
