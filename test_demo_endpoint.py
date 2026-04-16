#!/usr/bin/env python3
"""Test connection with demo endpoint"""

import os
from dotenv import load_dotenv
import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
secret_key = os.getenv("BINANCE_SECRET_KEY")
base_url = os.getenv("BINANCE_TESTNET_BASE_URL")

print("=" * 60)
print("TESTING WITH DEMO ENDPOINT")
print("=" * 60)
print(f"Base URL: {base_url}\n")

try:
    # Test 1: Ping
    print("[1] Testing ping...")
    response = requests.get(f"{base_url}/fapi/v1/ping", timeout=5)
    print(f"    Status: {response.status_code} ✓\n")
    
    # Test 2: Account info
    print("[2] Testing account info...")
    params = {"timestamp": int(time.time() * 1000)}
    query_string = urlencode(params)
    signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
    params["signature"] = signature
    
    headers = {"X-MBX-APIKEY": api_key}
    
    response = requests.get(
        f"{base_url}/fapi/v1/account",
        params=params,
        headers=headers,
        timeout=5
    )
    
    print(f"    Status: {response.status_code}")
    
    if response.status_code == 200:
        account = response.json()
        print(f"    ✓ Account connected successfully!\n")
        
        # Get USDT balance
        for asset in account.get("assets", []):
            if asset["asset"] == "USDT":
                balance = asset.get("availableBalance", 0)
                print(f"    ✓ USDT Balance: {balance}")
                break
        print("\n" + "=" * 60)
        print("✅ CONNECTION SUCCESSFUL!")
        print("=" * 60)
    else:
        print(f"    Error: {response.status_code}")
        print(f"    Response: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ Error: {str(e)}")
    import traceback
    traceback.print_exc()
