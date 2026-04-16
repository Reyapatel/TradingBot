#!/usr/bin/env python3
"""
Command-line interface for the trading bot.
Users interact with the bot through this CLI interface.
"""

import argparse
import json
from typing import Optional
from bot import BinanceFuturesClient, OrderManager, setup_logging
from bot.logging_config import setup_logging as setup_logger

# Initialize logger
logger = setup_logger()


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    Create and configure argument parser for CLI.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        description="Simplified Trading Bot for Binance Futures Testnet",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a market buy order for 0.1 BTC
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.1
  
  # Place a limit sell order for 1 ETH at 2500 USDT
  python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 1 --price 2500
  
  # Get account balance
  python cli.py --account-info
        """
    )
    
    # Order placement arguments
    parser.add_argument(
        "--symbol",
        type=str,
        help="Trading symbol (e.g., BTCUSDT, ETHUSDT)",
    )
    
    parser.add_argument(
        "--side",
        type=str,
        choices=["BUY", "SELL"],
        help="Order side: BUY or SELL",
    )
    
    parser.add_argument(
        "--type",
        type=str,
        choices=["MARKET", "LIMIT"],
        dest="order_type",
        help="Order type: MARKET or LIMIT",
    )
    
    parser.add_argument(
        "--quantity",
        "-q",
        type=float,
        help="Order quantity",
    )
    
    parser.add_argument(
        "--price",
        "-p",
        type=float,
        help="Order price (required for LIMIT orders)",
    )
    
    # Account information arguments
    parser.add_argument(
        "--account-info",
        action="store_true",
        help="Display account information",
    )
    
    parser.add_argument(
        "--balance",
        "-b",
        action="store_true",
        help="Display USDT balance",
    )
    
    # Output formatting
    parser.add_argument(
        "--json",
        "-j",
        action="store_true",
        help="Output in JSON format",
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )
    
    return parser


def format_output(data: dict, as_json: bool = False) -> str:
    """
    Format output for display.
    
    Args:
        data: Data dictionary to format
        as_json: If True, return JSON format
    
    Returns:
        Formatted output string
    """
    if as_json:
        return json.dumps(data, indent=2)
    
    return format_output_pretty(data)


def format_output_pretty(data: dict, indent: int = 0) -> str:
    """
    Format output in human-readable format.
    
    Args:
        data: Data dictionary to format
        indent: Indentation level
    
    Returns:
        Formatted output string
    """
    lines = []
    prefix = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(format_output_pretty(value, indent + 1))
        elif isinstance(value, (list, tuple)):
            lines.append(f"{prefix}{key}: {value}")
        else:
            lines.append(f"{prefix}{key}: {value}")
    
    return "\n".join(lines)


def main():
    """Main CLI entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    # Setup logging
    log_level = "DEBUG" if args.verbose else "INFO"
    logger = setup_logger(log_level=log_level)
    
    try:
        # Initialize Binance client
        client = BinanceFuturesClient()
        order_manager = OrderManager(client)
        
        # Handle account info requests
        if args.account_info:
            print("\n" + "="*60)
            print("ACCOUNT INFORMATION")
            print("="*60)
            account_data = client.get_account()
            output = format_output(account_data, args.json)
            print(output)
            return
        
        # Handle balance requests
        if args.balance:
            balance = client.get_balance("USDT")
            print("\n" + "="*60)
            print(f"USDT BALANCE: {balance:.2f}")
            print("="*60)
            return
        
        # Handle order placement
        if args.symbol and args.side and args.order_type and args.quantity is not None:
            
            # Validate required inputs
            if args.order_type == "LIMIT" and args.price is None:
                print("\n❌ ERROR: Price is required for LIMIT orders")
                parser.print_help()
                return
            
            print("\n" + "="*60)
            print("PLACING ORDER")
            print("="*60)
            
            # Place order
            result = order_manager.place_order(
                symbol=args.symbol,
                side=args.side,
                order_type=args.order_type,
                quantity=args.quantity,
                price=args.price
            )
            
            # Display result
            output = format_output(result, args.json)
            print(output)
            
            # Print status with emoji
            if result["status"] == "SUCCESS":
                print("\n✅ Order placed successfully!")
            else:
                print("\n❌ Order placement failed!")
            
            print("="*60)
            return
        
        # If no command provided, show help
        parser.print_help()
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        logger.info("Operation cancelled by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        logger.error(f"Fatal error: {str(e)}", exc_info=True)


if __name__ == "__main__":
    main()
