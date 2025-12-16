import asyncio
import json
from datetime import datetime
import websockets
from storage.db import insert_tick

BINANCE_FUTURES_WS = "wss://fstream.binance.com/ws"


async def stream_symbol(symbol: str):
    url = f"{BINANCE_FUTURES_WS}/{symbol}@trade"
    async with websockets.connect(url) as ws:
        async for message in ws:
            try:
                data = json.loads(message)
                if data.get("e") == "trade":
                    ts = datetime.fromtimestamp(
                        (data.get("T") or data.get("E")) / 1000
                    ).isoformat()

                    symbol = data.get("s")
                    price = float(data.get("p"))
                    size = float(data.get("q"))

                    insert_tick(ts, symbol, price, size)
            except Exception:
                continue


async def start_stream(symbols):
    tasks = [stream_symbol(sym.lower()) for sym in symbols]
    await asyncio.gather(*tasks)
