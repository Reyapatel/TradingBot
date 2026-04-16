#!/usr/bin/env python3
"""
Simple script to test Binance Futures Testnet connection
"""

import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
secret_key = os.getenv("BINANCE_SECRET_KEY")

print("=" * 60)
print("TESTING TESTNET CONNECTIVITY")
print("=" * 60)

try:
    # Test 1: Ping endpoint (no auth required)
    print("\n[1] Testing testnet ping...")
    response = requests.get("https://testnet.binancefuture.com/fapi/v1/ping", timeout=5)
    print(f"    ✓ Testnet is accessible: {response.status_code}")
    
    # Test 2: Time endpoint (no auth required)
    print("[2] Testing server time...")
    response = requests.get("https://testnet.binancefuture.com/fapi/v1/time", timeout=5)
    server_time = response.json().get("serverTime")
    print(f"    ✓ Server time: {server_time}")
    
    # Test 3: Account endpoint (auth required)
    print("[3] Testing account info with API key...")
    params = {"timestamp": int(time.time() * 1000)}
    query_string = urlencode(params)
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    
    headers = {"X-MBX-APIKEY": api_key}
    
    response = requests.get(
        "https://testnet.binancefuture.com/fapi/v1/account",
        params=params,
        headers=headers,
        timeout=5
    )
    
    print(f"    Response Status: {response.status_code}")
    
    if response.status_code == 200:
        account = response.json()
        print(f"    ✓ Account connected successfully!")
        
        # Get USDT balance
        for asset in account.get("assets", []):
            if asset["asset"] == "USDT":
                balance = asset.get("availableBalance", 0)
                print(f"    ✓ USDT Balance: {balance}")
                break
    else:
        print(f"    ❌ Status: {response.status_code}")
        print(f"    Response: {response.text[:300]}")
    
    print("\n" + "=" * 60)
    
except requests.exceptions.Timeout:
    print("❌ Request timeout - testnet might be down")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - check your internet or testnet URL")
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
