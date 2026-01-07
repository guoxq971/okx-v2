from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel
import os
from okx_client import OKXClient

load_dotenv()

app = FastAPI()

class OrderRequest(BaseModel):
    instId: str
    tdMode: str
    side: str
    ordType: str
    sz: str
    px: str = None

class APIConfig(BaseModel):
    api_key: str
    secret_key: str
    passphrase: str
    is_simulated: bool = False

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OKX Client
api_key = os.getenv("OKX_API_KEY")
secret_key = os.getenv("OKX_SECRET_KEY")
passphrase = os.getenv("OKX_PASSPHRASE")
is_simulated = os.getenv("OKX_SIMULATED", "0") == "1"

client = OKXClient(api_key, secret_key, passphrase, is_simulated)

@app.get("/")
async def root():
    return {"message": "OKX 交易 API 正在运行"}

@app.post("/api/config")
async def update_config(config: APIConfig):
    global client, api_key, secret_key, passphrase, is_simulated
    
    # Update global variables
    api_key = config.api_key
    secret_key = config.secret_key
    passphrase = config.passphrase
    is_simulated = config.is_simulated
    
    # Update Client
    client = OKXClient(api_key, secret_key, passphrase, is_simulated)
    
    # Update .env file
    env_content = f"""OKX_API_KEY={api_key}
OKX_SECRET_KEY={secret_key}
OKX_PASSPHRASE={passphrase}
OKX_SIMULATED={'1' if is_simulated else '0'}
"""
    try:
        with open(".env", "w") as f:
            f.write(env_content)
    except Exception as e:
        print(f"Failed to write .env file: {e}")
        
    return {"message": "API 配置已更新"}

@app.get("/api/config")
async def get_config():
    # Only return existence of keys, not the actual keys for security (or maybe partial)
    # For this local app, returning full config might be okay for UX, but let's be safe-ish
    # Actually, for a local tool, user wants to see what they typed.
    return {
        "api_key": api_key,
        "secret_key": secret_key,
        "passphrase": passphrase,
        "is_simulated": is_simulated
    }

@app.get("/api/tickers")
async def get_tickers(instType: str = "SPOT"):
    """
    Get all tickers.
    instType: SPOT, SWAP, FUTURES, OPTION
    """
    res = await client.get_tickers(instType)
    if res.get("code") == "0":
        return res["data"]
    else:
        print(f"Error fetching tickers: {res}")
        raise HTTPException(status_code=400, detail=res.get("msg", "获取行情失败"))

@app.get("/api/candles")
async def get_candles(instId: str, bar: str = "1H"):
    res = await client.get_candles(instId, bar)
    if res.get("code") == "0":
        return res["data"]
    else:
        raise HTTPException(status_code=400, detail=res.get("msg", "获取K线失败"))

@app.get("/api/instruments")
async def get_instruments(instType: str = "SPOT"):
    """
    Get instruments details (to map base/quote currencies).
    """
    res = await client.get_instruments(instType)
    if res.get("code") == "0":
        return res["data"]
    else:
        raise HTTPException(status_code=400, detail=res.get("msg", "获取币种信息失败"))

@app.get("/api/balance")
async def get_balance():
    res = await client.get_balance()
    if res.get("code") == "0":
        return res["data"][0] if res["data"] else {}
    else:
        print(f"Error fetching balance: {res}")
        # If API key is not set or invalid
        if not api_key:
             return {"details": [], "totalEq": "0", "note": "API Key 未配置"}
        raise HTTPException(status_code=400, detail=res.get("msg", "获取余额失败"))

@app.get("/api/positions")
async def get_positions():
    res = await client.get_positions()
    if res.get("code") == "0":
        return res["data"]
    else:
        if not api_key:
             return []
        raise HTTPException(status_code=400, detail=res.get("msg", "获取持仓失败"))

@app.post("/api/trade")
async def trade(order: OrderRequest):
    res = await client.place_order(
        instId=order.instId,
        tdMode=order.tdMode,
        side=order.side,
        ordType=order.ordType,
        sz=order.sz,
        px=order.px
    )
    if res.get("code") == "0":
        return res["data"][0]
    else:
        raise HTTPException(status_code=400, detail=res.get("msg", "下单失败"))

@app.get("/api/orders/pending")
async def get_orders_pending(instType: str = None):
    # Fetch Standard Orders
    res_std = await client.get_orders_pending(instType)
    std_orders = res_std.get("data", []) if res_std.get("code") == "0" else []
    
    # Fetch Algo Orders (TP/SL, Trigger, etc.)
    res_algo = await client.get_orders_algo_pending(instType)
    algo_orders = res_algo.get("data", []) if res_algo.get("code") == "0" else []
    
    # Process Algo Orders to match Standard Order structure for Frontend
    processed_algo = []
    for order in algo_orders:
        # Algo orders use 'algoId' instead of 'ordId'
        # They might have 'triggerPx' instead of 'px' or similar differences
        order['ordId'] = order.get('algoId') 
        order['isAlgo'] = True # Flag for frontend if needed
        # Ensure state is mapped if needed (algo usually 'live' or 'effective')
        processed_algo.append(order)
        
    # Merge both
    return std_orders + processed_algo

@app.get("/api/orders/history")
async def get_orders_history(instType: str = None):
    res = await client.get_orders_history(instType)
    if res.get("code") == "0":
        return res["data"]
    else:
        print(f"Error fetching history orders: {res}")
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
