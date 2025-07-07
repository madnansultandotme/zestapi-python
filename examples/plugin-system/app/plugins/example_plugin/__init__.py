"""
Example Plugin for ZestAPI
Demonstrates request logging and custom middleware
"""

from .plugin import RequestLoggerPlugin

__version__ = "1.0.0"
__plugin_name__ = "request_logger"
__plugin_class__ = RequestLoggerPlugin

__all__ = ["RequestLoggerPlugin"]
