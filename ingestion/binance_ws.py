import asyncio
import json
from datetime import datetime
import websockets
from storage.db import insert_tick
import logging

BINANCE_FUTURES_WS = "wss://fstream.binance.com/ws"

logger = logging.getLogger(__name__)


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
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error for {symbol}: {e}")
            except Exception as e:
                logger.error(f"Unexpected error processing {symbol}: {e}")
                continue


async def start_stream(symbols):
    tasks = [stream_symbol(sym.lower()) for sym in symbols]
    await asyncio.gather(*tasks)
