"""
Configuration File
Change these values without touching the main code.
"""

# ==========================
# Market Data Settings
# ==========================

DEFAULT_PERIOD = "5D"
DEFAULT_INTERVAL = "15m"
DEFAULT_MA = 50

# ==========================
# Resample Timeframes
# ==========================

TIMEFRAMES = {
    "45min": "45min",
    "90min": "90min",
    "180min": "180min",
}

# ==========================
# Indicators
# ==========================

RSI_PERIOD = 14
ADX_PERIOD = 14

RSI_UPTREND = 50
RSI_DOWNTREND = 55

ADX_THRESHOLD = 40

# ==========================
# File Paths
# ==========================

SYMBOL_FILE = "data/nse_symbols.csv"
EXPORT_FILE = "data/Trend_Output.xlsx"

# ==========================
# Plot Settings
# ==========================

DEFAULT_CHART_DAYS = 4