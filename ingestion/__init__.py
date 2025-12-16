"""
Data ingestion module for real-time market data collection.
"""
from .binance_ws import start_stream, stream_symbol

__all__ = ['start_stream', 'stream_symbol']
