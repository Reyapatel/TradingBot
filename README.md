# Simplified Trading Bot for Binance Futures Testnet

A professional-grade Python CLI application that places orders on Binance Futures Testnet. Built with clean, modular architecture following best practices.

## 🎯 Features

- ✅ **Market Orders** - Place instant market orders
- ✅ **Limit Orders** - Place orders at specific prices
- ✅ **BUY & SELL** - Both order sides supported
- ✅ **Account Management** - Check balance and account info
- ✅ **Comprehensive Validation** - Input validation before API calls
- ✅ **Detailed Logging** - File and console logging for debugging
- ✅ **Error Handling** - Graceful error handling with meaningful messages
- ✅ **JSON Output** - Optional JSON formatting for integration
- ✅ **Testnet Safe** - Uses Binance Futures Testnet (no real money)

## 📋 Prerequisites

- **Python 3.8+** - Required for type hints and modern syntax
- **pip** - Python package manager
- **Binance Futures Testnet Account** - [Create here](https://testnet.binancefuture.com)
- **Testnet API Keys** - Generate in account settings

## 🚀 Quick Start

### 1. Clone and Setup

```bash
cd /Users/patelreya/Downloads/trading_bot
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your testnet API credentials
# BINANCE_API_KEY=your_testnet_key
# BINANCE_SECRET_KEY=your_testnet_secret
```

**🔐 How to get Testnet API Keys:**
1. Go to https://testnet.binancefuture.com
2. Log in with your account
3. Account → API Management
4. Create new API key
5. Copy key and secret to `.env` file

### 4. Run Your First Order

```bash
# Check account balance
python cli.py --balance

# Place a market buy order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.1

# Place a limit sell order
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 1 --price 2500
```

## 📖 Usage Guide

### Basic Commands

```bash
# Market Buy
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.1

# Market Sell
python cli.py --symbol BTCUSDT --side SELL --type MARKET --quantity 0.1

# Limit Buy
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.1 --price 45000

# Limit Sell
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.1 --price 50000
```

### Account Commands

```bash
# Display USDT balance
python cli.py --balance

# Display full account information
python cli.py --account-info
```

### Output Formatting

```bash
# Output in JSON format (useful for scripting)
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.1 --json

# Enable verbose logging (DEBUG level)
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.1 --verbose
```

### Get Help

```bash
python cli.py --help
```

## 📁 Project Structure

```
trading_bot/
├── bot/                          # Core trading bot package
│   ├── __init__.py              # Package initialization
│   ├── client.py                # Binance API wrapper (authenticates & communicates)
│   ├── orders.py                # Order placement logic
│   ├── validators.py            # Input validation layer
│   └── logging_config.py        # Centralized logging setup
│
├── cli.py                        # Command-line interface (user facing)
├── .env.example                 # Environment variables template
├── requirements.txt             # Python dependencies
├── README.md                    # This file
└── logs/                        # Auto-created log files
    └── trading_bot.log          # Application logs
```

## 🏗️ Architecture

### Separation of Concerns

| Component | Responsibility |
|-----------|-----------------|
| `client.py` | Pure API communication with Binance |
| `orders.py` | Business logic for order placement |
| `validators.py` | Input validation (catches errors early) |
| `cli.py` | User interface layer |
| `logging_config.py` | Logging infrastructure |

### Data Flow

```
User (CLI)
    ↓
cli.py (parses arguments)
    ↓
validators.py (validates inputs)
    ↓
orders.py (executes order logic)
    ↓
client.py (sends API request to Binance)
    ↓
Binance API
```

## 🔒 Security Best Practices

✅ **API Keys in .env** - Never commit `.env` to git
✅ **Testnet Only** - Uses testnet (no real money)
✅ **HMAC-SHA256** - Proper request signing
✅ **Timestamped Requests** - Prevents replay attacks
✅ **Error Handling** - Doesn't expose sensitive data

## 📝 API Response Examples

### Successful Market Order
```json
{
  "status": "SUCCESS",
  "message": "Order placed successfully",
  "order_request": {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "type": "MARKET",
    "quantity": 0.1,
    "price": null
  },
  "order_response": {
    "order_id": 12345678,
    "status": "FILLED",
    "executed_quantity": 0.1,
    "fill_price": 45234.50,
    "total_cost": 4523.45,
    "timestamp": 1634567890123
  }
}
```

### Failed Order (Price Required for Limit)
```json
{
  "status": "FAILURE",
  "message": "Validation error: Price is required for LIMIT orders",
  "error_type": "VALIDATION_ERROR"
}
```

## 📚 Logging

Logs are automatically created in `logs/trading_bot.log`

```
2024-04-16 10:30:45 - trading_bot - INFO - BinanceFuturesClient initialized
2024-04-16 10:30:46 - trading_bot - INFO - Placing BUY MARKET order: BTCUSDT x 0.1
2024-04-16 10:30:47 - trading_bot - INFO - Order placed successfully. Order ID: 12345678
```

## 🧪 Testing Checklist

Before submission, test:

- [ ] Market Buy order
- [ ] Market Sell order
- [ ] Limit Buy order
- [ ] Limit Sell order
- [ ] Account balance display
- [ ] Invalid symbol handling
- [ ] Missing price for LIMIT order
- [ ] Wrong side/type values
- [ ] Large quantity validation

## ⚙️ Requirements

See `requirements.txt`:

```
python-binance==1.0.17    # Binance API wrapper
python-dotenv==1.0.0      # Environment variable management
requests==2.31.0          # HTTP requests
```

## 📖 Documentation

### Class Documentation

#### BinanceFuturesClient
```python
from bot import BinanceFuturesClient

client = BinanceFuturesClient()
account = client.get_account()
balance = client.get_balance("USDT")
order = client.place_order("BTCUSDT", "BUY", "MARKET", 0.1)
```

#### OrderManager
```python
from bot import BinanceFuturesClient, OrderManager

client = BinanceFuturesClient()
manager = OrderManager(client)
result = manager.place_order("BTCUSDT", "BUY", "MARKET", 0.1)
```

## 🐛 Troubleshooting

### "API key and secret key are required"
**Solution:** Check `.env` file has valid testnet credentials

```bash
# Verify .env file exists
ls -la .env

# Check it has your keys
cat .env
```

### "Invalid symbol format"
**Solution:** Symbol must be uppercase

```bash
# ❌ Wrong
python cli.py --symbol btcusdt --side BUY --type MARKET --quantity 0.1

# ✅ Correct
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.1
```

### "Price is required for LIMIT orders"
**Solution:** Add `--price` argument for LIMIT orders

```bash
# ✅ Correct
python cli.py --symbol BTCUSDT --side BUY --type LIMIT --quantity 0.1 --price 45000
```

### Connection Timeout
**Solution:** Testnet might be down temporarily. Check https://testnet.binancefuture.com

## 📊 Code Quality

- ✅ Type hints throughout
- ✅ Comprehensive docstrings
- ✅ Clean error handling
- ✅ Modular architecture
- ✅ Professional logging
- ✅ Input validation
- ✅ PEP 8 compliant

## 🎓 Learning Resources

- [Binance Futures API Docs](https://binance-docs.github.io/apidocs/futures/en/)
- [python-binance Documentation](https://python-binance.readthedocs.io/)
- [HMAC Authentication](https://en.wikipedia.org/wiki/HMAC)

## 📞 Support

If you encounter issues:

1. Check logs: `tail logs/trading_bot.log`
2. Run with verbose flag: `--verbose`
3. Verify API keys in `.env`
4. Ensure virtual environment is active: `(venv)` in terminal
5. Check Testnet status

## 📄 License

Educational project for learning purposes.

## 👤 Author

Your Name (Internship Project)

---

**Made with ❤️ for learning and professional development**
