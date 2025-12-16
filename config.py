"""
Configuration constants for the Quant Analytics Dashboard.
"""

# ==================== DATABASE ====================
DB_PATH = "data/ticks.db"
DB_ECHO = False  # Set to True for SQL query logging

# ==================== WEBSOCKET ====================
BINANCE_FUTURES_WS = "wss://fstream.binance.com/ws"
WS_TIMEOUT_SECONDS = 1.0  # Check stop_event every N seconds

# ==================== ANALYTICS ====================

# Minimum data points required for analytics
MIN_REGRESSION_POINTS = 40  # OLS requires adequate degrees of freedom
MIN_ADF_OBSERVATIONS = 20   # Minimum for reliable ADF test
MIN_CORRELATION_WINDOW = 10  # Minimum window for correlation

# Default parameter values
DEFAULT_ROLLING_WINDOW = 50
DEFAULT_ALERT_THRESHOLD = 2.0
DEFAULT_LOOKBACK_MINUTES = 60

# Valid timeframe mappings
VALID_TIMEFRAMES = {
    "1s": "1S",   # 1 second
    "1m": "1T",   # 1 minute (T = minute in pandas)
    "5m": "5T"    # 5 minutes
}

# ==================== UI ====================
PAGE_TITLE = "Quant Analytics App"
PAGE_LAYOUT = "wide"

# Default symbols for initial load
DEFAULT_SYMBOLS = "btcusdt,ethusdt"

# Chart heights (in pixels)
CHART_HEIGHT_STANDARD = 400
CHART_HEIGHT_TALL = 450

# ==================== LOGGING ====================
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# ==================== EXPORT ====================
CSV_ENCODING = "utf-8"
CSV_INDEX = False
