"""
Order management logic for the trading bot.
Handles order placement and response formatting.
"""

from typing import Dict, Any
from bot.client import BinanceFuturesClient, BinanceAPIError
from bot.validators import validate_order_inputs, ValidationError
from bot.logging_config import setup_logging

# Initialize logger
logger = setup_logging()


class OrderManager:
    """
    Manages order placement and tracking for Binance Futures trading.
    Wraps the client and adds business logic.
    """
    
    def __init__(self, client: BinanceFuturesClient):
        """
        Initialize order manager.
        
        Args:
            client: BinanceFuturesClient instance
        """
        self.client = client
        logger.info("OrderManager initialized")
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None
    ) -> Dict[str, Any]:
        """
        Place an order with full validation and error handling.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            order_type: Order type (MARKET or LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
        
        Returns:
            Dictionary containing order result with metadata
        
        Raises:
            ValidationError: If inputs are invalid
            BinanceAPIError: If API call fails
        """
        try:
            # Validate all inputs
            symbol, side, order_type, quantity, price = validate_order_inputs(
                symbol, side, order_type, quantity, price
            )
            
            logger.info(f"Validated inputs: {symbol} {side} {order_type} x {quantity}")
            
            # Place order via API
            order_response = self.client.place_order(
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price
            )
            
            # Format response
            result = self._format_success_response(order_response, symbol, side, order_type, quantity, price)
            
            logger.info(f"Order placement successful: {result}")
            
            return result
            
        except ValidationError as e:
            error_msg = f"Validation error: {str(e)}"
            logger.error(error_msg)
            return self._format_error_response(error_msg, "VALIDATION_ERROR")
        
        except BinanceAPIError as e:
            error_msg = f"API error: {str(e)}"
            logger.error(error_msg)
            return self._format_error_response(error_msg, "API_ERROR")
        
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.error(error_msg)
            return self._format_error_response(error_msg, "UNKNOWN_ERROR")
    
    def _format_success_response(
        self,
        order_response: Dict[str, Any],
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float
    ) -> Dict[str, Any]:
        """
        Format order response for display.
        
        Args:
            order_response: Raw response from Binance API
            symbol: Trading symbol
            side: Order side
            order_type: Order type
            quantity: Order quantity
            price: Order price
        
        Returns:
            Formatted response dictionary
        """
        return {
            "status": "SUCCESS",
            "message": "Order placed successfully",
            "order_request": {
                "symbol": symbol,
                "side": side,
                "type": order_type,
                "quantity": quantity,
                "price": price if order_type == "LIMIT" else None,
            },
            "order_response": {
                "order_id": order_response.get("orderId"),
                "status": order_response.get("status"),
                "executed_quantity": float(order_response.get("executedQty", 0)),
                "fill_price": self._get_fill_price(order_response),
                "total_cost": self._calculate_total_cost(order_response),
                "timestamp": order_response.get("time"),
            },
            "timestamp": order_response.get("updateTime")
        }
    
    def _format_error_response(
        self,
        error_message: str,
        error_type: str
    ) -> Dict[str, Any]:
        """
        Format error response for display.
        
        Args:
            error_message: Error message
            error_type: Type of error
        
        Returns:
            Formatted error response dictionary
        """
        return {
            "status": "FAILURE",
            "message": error_message,
            "error_type": error_type,
        }
    
    @staticmethod
    def _get_fill_price(order_response: Dict[str, Any]) -> float:
        """
        Calculate average fill price from order response.
        
        Args:
            order_response: Order response from API
        
        Returns:
            Average fill price or 0 if not filled
        """
        executed_qty = float(order_response.get("executedQty", 0))
        cum_quote = float(order_response.get("cumQuote", 0))
        
        if executed_qty > 0:
            return cum_quote / executed_qty
        return 0.0
    
    @staticmethod
    def _calculate_total_cost(order_response: Dict[str, Any]) -> float:
        """
        Calculate total cost (for buys) or proceeds (for sells).
        
        Args:
            order_response: Order response from API
        
        Returns:
            Total cost/proceeds
        """
        return float(order_response.get("cumQuote", 0))
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Check status of existing order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        
        Returns:
            Order status information
        """
        try:
            response = self.client.get_order(symbol, order_id)
            return {
                "status": "SUCCESS",
                "order_id": response.get("orderId"),
                "order_status": response.get("status"),
                "executed_quantity": float(response.get("executedQty", 0)),
                "remaining_quantity": float(response.get("origQty", 0)) - float(response.get("executedQty", 0)),
            }
        except BinanceAPIError as e:
            return {
                "status": "FAILURE",
                "message": str(e),
            }
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel existing order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        
        Returns:
            Cancellation result
        """
        try:
            response = self.client.cancel_order(symbol, order_id)
            return {
                "status": "SUCCESS",
                "message": "Order cancelled successfully",
                "order_id": response.get("orderId"),
                "remaining_quantity": float(response.get("origQty", 0)) - float(response.get("executedQty", 0)),
            }
        except BinanceAPIError as e:
            return {
                "status": "FAILURE",
                "message": str(e),
            }
