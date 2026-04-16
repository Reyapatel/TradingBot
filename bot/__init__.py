"""
Trading Bot Package
A simplified trading bot for Binance Futures Testnet.
"""

from bot.client import BinanceFuturesClient, BinanceAPIError
from bot.orders import OrderManager
from bot.validators import ValidationError, validate_order_inputs
from bot.logging_config import setup_logging

__version__ = "1.0.0"
__author__ = "Your Name"

__all__ = [
    "BinanceFuturesClient",
    "OrderManager",
    "BinanceAPIError",
    "ValidationError",
    "validate_order_inputs",
    "setup_logging",
]
