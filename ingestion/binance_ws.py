import asyncio
import json
from datetime import datetime
import websockets
from storage.db import insert_tick
import logging

BINANCE_FUTURES_WS = "wss://fstream.binance.com/ws"

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def stream_symbol(symbol: str, stop_event):
    """
    Stream trade data for a single symbol from Binance Futures WebSocket.

    Args:
        symbol: Trading pair symbol (lowercase, e.g., 'btcusdt')
        stop_event: Threading event to signal shutdown
    """
    url = f"{BINANCE_FUTURES_WS}/{symbol}@trade"

    try:
        async with websockets.connect(url) as ws:
            logger.info(f"WebSocket connected: {symbol}")

            while not stop_event.is_set():
                try:
                    # Set timeout to check stop_event periodically
                    message = await asyncio.wait_for(ws.recv(), timeout=1.0)

                    try:
                        data = json.loads(message)

                        if data.get("e") == "trade":
                            # Extract timestamp (T = trade time, E = event time)
                            ts = datetime.fromtimestamp(
                                (data.get("T") or data.get("E")) / 1000
                            ).isoformat()

                            symbol_name = data.get("s")
                            price = float(data.get("p"))
                            size = float(data.get("q"))

                            # Insert into database
                            insert_tick(ts, symbol_name, price, size)

                    except json.JSONDecodeError as e:
                        logger.warning(f"JSON decode error for {symbol}: {e}")
                    except (KeyError, ValueError, TypeError) as e:
                        logger.warning(f"Data parsing error for {symbol}: {e}")
                    except Exception as e:
                        logger.error(f"Unexpected error processing {symbol}: {e}")

                except asyncio.TimeoutError:
                    # Normal timeout, check stop_event and continue
                    continue
                except websockets.exceptions.ConnectionClosed:
                    logger.warning(f"WebSocket connection closed for {symbol}")
                    break

    except Exception as e:
        logger.error(f"WebSocket error for {symbol}: {e}")
    finally:
        logger.info(f"WebSocket stream ended for {symbol}")


async def start_stream(symbols, stop_event=None):
    """
    Start WebSocket streams for multiple symbols.

    Args:
        symbols: List of trading pair symbols (lowercase)
        stop_event: Optional threading event to signal shutdown
    """
    if stop_event is None:
        # Create a dummy event that's never set for backward compatibility
        import threading
        stop_event = threading.Event()

    tasks = [stream_symbol(sym.lower(), stop_event) for sym in symbols]

    try:
        await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        logger.error(f"Stream error: {e}")
