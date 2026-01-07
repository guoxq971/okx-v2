import httpx
import asyncio

async def test_okx():
    url = "https://www.okx.com/api/v5/market/tickers?instType=SPOT"
    print(f"Testing connection to {url}...")
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            print(f"Status: {resp.status_code}")
            print(f"Data: {resp.text[:100]}...")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_okx())
