import httpx
import time
import hmac
import base64
import hashlib
import json
import os
from datetime import datetime
from urllib.parse import urlencode

class OKXClient:
    def __init__(self, api_key=None, secret_key=None, passphrase=None, is_simulated=False):
        self.base_url = "https://www.okx.com"
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        self.is_simulated = is_simulated # If we want to use demo trading later

    def _get_timestamp(self):
        return datetime.utcnow().isoformat()[:-3] + 'Z'
    
    def _sign(self, timestamp, method, request_path, body=''):
        message = f"{timestamp}{method}{request_path}{body}"
        mac = hmac.new(
            bytes(self.secret_key, encoding='utf-8'),
            bytes(message, encoding='utf-8'),
            digestmod=hashlib.sha256
        )
        return base64.b64encode(mac.digest()).decode('utf-8')

    def _get_headers(self, method, request_path, body=''):
        if not self.api_key:
            return {}
            
        timestamp = datetime.utcnow().isoformat(timespec='milliseconds') + 'Z'
        sign = self._sign(timestamp, method, request_path, body)
        
        headers = {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': sign,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json',
            'x-simulated-trading': '1' if self.is_simulated else '0'
        }
        return headers

    async def _request(self, method, path, params=None, body=None, private=False):
        url = f"{self.base_url}{path}"
        
        # Prepare body for signature
        body_str = ''
        if body:
            body_str = json.dumps(body)
        
        # Prepare query params
        if params:
            query_string = urlencode(params)
            path_with_query = f"{path}?{query_string}"
        else:
            path_with_query = path

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }
        if private:
            private_headers = self._get_headers(method, path_with_query, body_str)
            headers.update(private_headers)
        
        # Configure proxy if environment variable is set
        proxy = os.getenv("HTTPS_PROXY") or os.getenv("HTTP_PROXY")
        
        async with httpx.AsyncClient(verify=False, proxy=proxy) as client:
            try:
                print(f"Requesting: {method} {url}")
                if method == 'GET':
                    response = await client.get(url, params=params, headers=headers, timeout=30.0)
                elif method == 'POST':
                    response = await client.post(url, content=body_str, headers=headers, timeout=30.0)
                
                print(f"Response Status: {response.status_code}")
                try:
                    data = response.json()
                    if data.get("code") != "0":
                         print(f"API Error Response: {data}")
                    return data
                except Exception as e:
                    print(f"JSON Decode Error: {response.text}")
                    return {"code": "500", "msg": f"JSON Decode Error: {str(e)}", "data": []}
                    
            except Exception as e:
                print(f"OKX API Request Error: {e}")
                return {"code": "500", "msg": str(e), "data": []}

    async def get_tickers(self, instType="SPOT"):
        # GET /api/v5/market/tickers
        return await self._request('GET', '/api/v5/market/tickers', params={'instType': instType})

    async def get_candles(self, instId, bar="1H"):
        # GET /api/v5/market/candles
        return await self._request('GET', '/api/v5/market/candles', params={'instId': instId, 'bar': bar})

    async def get_instruments(self, instType="SPOT"):
        # GET /api/v5/public/instruments
        return await self._request('GET', '/api/v5/public/instruments', params={'instType': instType})

    async def get_balance(self):
        # GET /api/v5/account/balance
        return await self._request('GET', '/api/v5/account/balance', private=True)

    async def get_positions(self):
        # GET /api/v5/account/positions
        return await self._request('GET', '/api/v5/account/positions', private=True)
    
    async def place_order(self, instId, tdMode, side, ordType, sz, px=None):
        # POST /api/v5/trade/order
        body = {
            "instId": instId,
            "tdMode": tdMode,
            "side": side,
            "ordType": ordType,
            "sz": sz
        }
        if px:
            body["px"] = px
            
        return await self._request('POST', '/api/v5/trade/order', body=body, private=True)

    async def get_orders_pending(self, instType=None):
        # GET /api/v5/trade/orders-pending
        params = {}
        if instType:
            params['instType'] = instType
        return await self._request('GET', '/api/v5/trade/orders-pending', params=params, private=True)

    async def get_orders_algo_pending(self, instType=None):
        # GET /api/v5/trade/orders-algo-pending
        # We must try fetching specific order types if generic fetch fails, 
        # but docs say ordType is optional for some, but required for others depending on mode?
        # Let's try explicit params for common types: stop, trigger, move_order_stop
        # Actually, let's fetch 'stop' (止盈止损) explicitly if general fails.
        # Wait, for orders-algo-pending, ordType IS REQUIRED.
        # "ordType: Order type. stop, trailing_stop, trigger, move_order_stop, twap, ice, oco"
        # We need to loop through them or ask for specific ones.
        # Let's try 'stop' (Stop Loss/Take Profit) and 'trigger' (Plan Order) which are most common.
        
        types = ['stop', 'trigger', 'oco', 'conditional'] 
        # Note: 'conditional' is sometimes used for plan orders in UI terms, but API uses 'trigger' usually?
        # OKX V5: 'trigger' is plan order, 'stop' is TP/SL attached to position? 
        # Actually 'stop' is often deprecated or specific.
        # Let's try 'conditional', 'oco', 'trigger', 'move_order_stop', 'twap'.
        
        # Let's just fetch 'trigger' (Plan) and 'oco' (One Cancels Other) and 'stop' (if valid).
        # To be safe, let's fetch 'stop', 'trigger', 'oco'.
        
        all_algos = []
         # Updated list of algo types to fetch
         # 'conditional' covers many UI-created Stop orders
         # 'move_order_stop' is Trailing Stop
         # 'twap', 'ice' are advanced
         algo_types = ['stop', 'trigger', 'oco', 'conditional', 'move_order_stop', 'twap']
         
         for o_type in algo_types:
              params = {'ordType': o_type}
              if instType:
                  params['instType'] = instType
              
              res = await self._request('GET', '/api/v5/trade/orders-algo-pending', params=params, private=True)
              if res.get("code") == "0":
                  all_algos.extend(res.get("data", []))
                  
         return {"code": "0", "data": all_algos, "msg": ""}

    async def get_orders_history(self, instType=None):
        # GET /api/v5/trade/orders-history
        # Note: default queries last 7 days.
        params = {}
        if instType:
            params['instType'] = instType
        # If no instType provided, OKX might require it or default to something.
        # But 'orders-history' usually requires instType or instId for efficiency, OR it returns mixed if allowed.
        # According to V5 docs: instType is REQUIRED for orders-history unless instId is provided.
        # So we default to SPOT or SWAP if not provided, or loop them?
        # Let's try SWAP as default since user is focused on contracts, or allow passing it.
        if not instType:
             params['instType'] = 'SWAP' # Default to SWAP for history
             
        return await self._request('GET', '/api/v5/trade/orders-history', params=params, private=True)
