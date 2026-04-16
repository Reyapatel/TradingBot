#!/usr/bin/env python3
"""Test different Binance API endpoints"""

import requests
import hmac
import hashlib
import time
from urllib.parse import urlencode
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("BINANCE_API_KEY")
secret_key = os.getenv("BINANCE_SECRET_KEY")

print("Testing alternative endpoints...\n")

# Try different endpoints
endpoints = [
    "/fapi/v2/account",
    "/fapi/v1/openOrders",
    "/fapi/v1/balance",
    "/fapi/v1/positionRisk",
]

for endpoint in endpoints:
    try:
        params = {"timestamp": int(time.time() * 1000)}
        query_string = urlencode(params)
        signature = hmac.new(secret_key.encode(), query_string.encode(), hashlib.sha256).hexdigest()
        params["signature"] = signature
        
        headers = {"X-MBX-APIKEY": api_key}
        
        response = requests.get(
            f"https://testnet.binancefuture.com{endpoint}",
            params=params,
            headers=headers,
            timeout=5
        )
        
        print(f"[{endpoint}]")
        print(f"  Status: {response.status_code}")
        if response.status_code != 200:
            print(f"  Error: {response.text[:150]}")
        else:
            print(f"  ✓ Success!")
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                print(f"  Items: {len(data)}")
            elif isinstance(data, dict):
                print(f"  Keys: {list(data.keys())[:5]}")
        print()
    except Exception as e:
        print(f"[{endpoint}] Error: {str(e)}\n")
