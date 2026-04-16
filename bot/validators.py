"""
Input validation for orders.
Ensures all user inputs are valid before sending to Binance.
"""

from enum import Enum
from typing import Tuple


class OrderSide(Enum):
    """Valid order sides."""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(Enum):
    """Valid order types."""
    MARKET = "MARKET"
    LIMIT = "LIMIT"


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


def validate_symbol(symbol: str) -> str:
    """
    Validate and normalize symbol format.
    
    Args:
        symbol: Trading symbol (e.g., BTCUSDT, ETHUSDT)
    
    Returns:
        Validated symbol in uppercase
    
    Raises:
        ValidationError: If symbol is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string")
    
    symbol = symbol.upper().strip()
    
    # Basic format check: should contain only letters and numbers
    if not symbol.isalnum():
        raise ValidationError(f"Invalid symbol format: {symbol}")
    
    # Should be at least 6 characters (e.g., BTCUSDT)
    if len(symbol) < 6:
        raise ValidationError(f"Symbol too short: {symbol}")
    
    return symbol


def validate_side(side: str) -> str:
    """
    Validate order side.
    
    Args:
        side: Either "BUY" or "SELL"
    
    Returns:
        Validated side in uppercase
    
    Raises:
        ValidationError: If side is invalid
    """
    if not side or not isinstance(side, str):
        raise ValidationError("Side must be a non-empty string")
    
    side = side.upper().strip()
    
    try:
        OrderSide[side]
        return side
    except KeyError:
        raise ValidationError(f"Invalid side: {side}. Must be BUY or SELL")


def validate_order_type(order_type: str) -> str:
    """
    Validate order type.
    
    Args:
        order_type: Either "MARKET" or "LIMIT"
    
    Returns:
        Validated order type in uppercase
    
    Raises:
        ValidationError: If order type is invalid
    """
    if not order_type or not isinstance(order_type, str):
        raise ValidationError("Order type must be a non-empty string")
    
    order_type = order_type.upper().strip()
    
    try:
        OrderType[order_type]
        return order_type
    except KeyError:
        raise ValidationError(f"Invalid order type: {order_type}. Must be MARKET or LIMIT")


def validate_quantity(quantity: float) -> float:
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity
    
    Returns:
        Validated quantity
    
    Raises:
        ValidationError: If quantity is invalid
    """
    try:
        quantity = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a number: {quantity}")
    
    if quantity <= 0:
        raise ValidationError(f"Quantity must be positive: {quantity}")
    
    # Check for reasonable maximum (prevent typos)
    if quantity > 1_000_000:
        raise ValidationError(f"Quantity unusually large: {quantity}")
    
    return quantity


def validate_price(price: float) -> float:
    """
    Validate limit order price.
    
    Args:
        price: Order price
    
    Returns:
        Validated price
    
    Raises:
        ValidationError: If price is invalid
    """
    try:
        price = float(price)
    except (ValueError, TypeError):
        raise ValidationError(f"Price must be a number: {price}")
    
    if price <= 0:
        raise ValidationError(f"Price must be positive: {price}")
    
    return price


def validate_order_inputs(
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: float = None
) -> Tuple[str, str, str, float, float]:
    """
    Validate all order inputs together.
    
    Args:
        symbol: Trading symbol
        side: Order side (BUY/SELL)
        order_type: Order type (MARKET/LIMIT)
        quantity: Order quantity
        price: Order price (required for LIMIT orders)
    
    Returns:
        Tuple of validated inputs
    
    Raises:
        ValidationError: If any input is invalid
    """
    # Validate individual inputs
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    order_type = validate_order_type(order_type)
    quantity = validate_quantity(quantity)
    
    # Validate price requirement for LIMIT orders
    if order_type == "LIMIT":
        if price is None:
            raise ValidationError("Price is required for LIMIT orders")
        price = validate_price(price)
    elif price is not None:
        # Warn if price provided for MARKET order, but still allow it
        price = None
    
    return symbol, side, order_type, quantity, price
