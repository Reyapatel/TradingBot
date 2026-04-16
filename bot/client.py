"""
Binance Futures API client wrapper.
Handles all communication with Binance Futures Testnet.
"""

import os
import hmac
import hashlib
import time
import requests
from typing import Dict, Any, Optional
from urllib.parse import urlencode
from dotenv import load_dotenv
from bot.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Initialize logger
logger = setup_logging()


class BinanceAPIError(Exception):
    """Custom exception for Binance API errors."""
    pass


class BinanceFuturesClient:
    """
    Client for interacting with Binance Futures Testnet API.
    Handles authentication and order placement.
    """
    
    def __init__(
        self,
        api_key: str = None,
        secret_key: str = None,
        base_url: str = None
    ):
        """
        Initialize Binance Futures client.
        
        Args:
            api_key: Binance API key (uses .env if not provided)
            secret_key: Binance secret key (uses .env if not provided)
            base_url: Base URL for API (uses .env if not provided)
        """
        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.secret_key = secret_key or os.getenv("BINANCE_SECRET_KEY")
        self.base_url = base_url or os.getenv("BINANCE_TESTNET_BASE_URL", "https://testnet.binancefuture.com")
        
        if not self.api_key or not self.secret_key:
            raise BinanceAPIError("API key and secret key are required. Check your .env file.")
        
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/json",
            "User-Agent": "trading-bot/1.0"
        })
        
        logger.info("BinanceFuturesClient initialized")
    
    def _generate_signature(self, params: Dict[str, Any]) -> str:
        """
        Generate HMAC SHA256 signature for API request.
        
        Args:
            params: Request parameters
        
        Returns:
            Signature string
        """
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature
    
    def _request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Binance API.
        
        Args:
            method: HTTP method (GET, POST, DELETE)
            endpoint: API endpoint path (e.g., /fapi/v1/order)
            params: Query/body parameters
        
        Returns:
            API response as dictionary
        
        Raises:
            BinanceAPIError: If API request fails
        """
        params = params or {}
        
        # Add timestamp
        params["timestamp"] = int(time.time() * 1000)
        
        # Generate signature
        signature = self._generate_signature(params)
        params["signature"] = signature
        
        # Set authorization header
        headers = self.session.headers.copy()
        headers["X-MBX-APIKEY"] = self.api_key
        
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                response = requests.get(url, params=params, headers=headers)
            elif method.upper() == "POST":
                response = requests.post(url, params=params, headers=headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, params=params, headers=headers)
            else:
                raise BinanceAPIError(f"Unsupported HTTP method: {method}")
            
            # Check for HTTP errors
            response.raise_for_status()
            
            data = response.json()
            
            # Check for API errors in response
            if "code" in data and data["code"] != 0 and "code" in data:
                error_msg = data.get("msg", "Unknown error")
                raise BinanceAPIError(f"API Error ({data['code']}): {error_msg}")
            
            logger.debug(f"{method} {endpoint} - Response: {data}")
            return data
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API Request failed: {str(e)}"
            logger.error(error_msg)
            raise BinanceAPIError(error_msg)
    
    def get_account(self) -> Dict[str, Any]:
        """
        Get account information.
        
        Returns:
            Account data dictionary
        
        Raises:
            BinanceAPIError: If request fails
        """
        logger.info("Fetching account information")
        try:
            # Try v1 endpoint first
            return self._request("GET", "/fapi/v1/account")
        except BinanceAPIError:
            # Fallback for demo endpoints that might not support v1
            logger.warning("Trying alternative account endpoint...")
            return self._request("GET", "/fapi/v2/account")
    
    def get_balance(self, asset: str = "USDT") -> float:
        """
        Get wallet balance for specific asset.
        
        Args:
            asset: Asset symbol (default: USDT)
        
        Returns:
            Balance amount
        
        Raises:
            BinanceAPIError: If request fails
        """
        account = self.get_account()
        
        for balance in account.get("assets", []):
            if balance["asset"] == asset:
                available = float(balance["availableBalance"])
                logger.info(f"{asset} balance: {available}")
                return available
        
        logger.warning(f"Asset {asset} not found in account")
        return 0.0
    
    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: float = None,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place an order on Binance Futures.
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
            side: Order side (BUY or SELL)
            order_type: Order type (MARKET or LIMIT)
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force (default: GTC - Good-Till-Cancel)
        
        Returns:
            Order response dictionary
        
        Raises:
            BinanceAPIError: If request fails
        """
        params = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
        }
        
        # Add price for limit orders
        if order_type == "LIMIT":
            params["price"] = price
            params["timeInForce"] = time_in_force
        
        logger.info(f"Placing {side} {order_type} order: {symbol} x {quantity}")
        
        response = self._request("POST", "/fapi/v1/order", params)
        
        logger.info(f"Order placed successfully. Order ID: {response.get('orderId')}")
        return response
    
    def get_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get order details.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        
        Returns:
            Order details dictionary
        
        Raises:
            BinanceAPIError: If request fails
        """
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        
        return self._request("GET", "/fapi/v1/order", params)
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        
        Returns:
            Cancellation response dictionary
        
        Raises:
            BinanceAPIError: If request fails
        """
        params = {
            "symbol": symbol,
            "orderId": order_id
        }
        
        logger.info(f"Cancelling order {order_id}")
        return self._request("DELETE", "/fapi/v1/order", params)
