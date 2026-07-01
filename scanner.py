"""
scanner.py

Scanner Engine

Responsibilities
----------------
1. Get F&O Symbols
2. Download OHLC
3. Calculate Moving Average
4. Detect Trend
5. Return Results DataFrame
"""

import pandas as pd

from fetch_data import (
    get_nse_symbols,
    get_stock_data,
)

from indicators import (
    sma,
)


# ==========================================================
# Trend Detection
# ==========================================================

def detect_trend(
    df: pd.DataFrame,
    ma_period: int,
):
    """
    Detect trend based on the latest candle.

    Returns
    -------
    trend
    candle
    trend_since
    """

    if len(df) < ma_period:
        return None

    ma_col = f"SMA_{ma_period}"

    trend = None
    trend_since = None

    #
    # Current Trend
    #

    if df.iloc[-1]["Close"] > df.iloc[-1][ma_col]:

        current = "up"

    else:

        current = "down"

    #
    # Find where trend started
    #

    for i in range(len(df) - 1, -1, -1):

        row = df.iloc[i]

        state = (
            "up"
            if row["Close"] > row[ma_col]
            else "down"
        )

        if state != current:

            if i + 1 < len(df):

                trend_since = df.index[i + 1]

            break

    #
    # Never changed
    #

    if trend_since is None:

        trend_since = df.index[0]

    #
    # Output
    #

    trend = (
        "Up Trend"
        if current == "up"
        else "Down Trend"
    )

    candle = (
        "🟢"
        if current == "up"
        else "🔴"
    )

    return {

        "Trend": trend,

        "Candle": candle,

        "Trend Since": trend_since.strftime(
            "%d-%b-%Y %H:%M"
        )

    }


# ==========================================================
# Scan One Symbol
# ==========================================================

def scan_symbol(
    symbol: str,
    period: str,
    interval: str,
    ma_period: int,
):
    """
    Scan a single stock.
    """

    try:

        df = get_stock_data(

            ticker=symbol,

            period=period,

            interval=interval,

        )

        df = sma(
            df,
            ma_period,
        )

        trend = detect_trend(

            df,

            ma_period,

        )

        if trend is None:

            return None

        return {

            "Symbol": symbol.replace(".NS", ""),

            "Trend": trend["Trend"],

            "Candle": trend["Candle"],

            "Trend Since": trend["Trend Since"],

        }

    except Exception:

        return None


# ==========================================================
# Scan Complete Market
# ==========================================================

def scan_market(
    period: str,
    interval: str,
    ma_period: int,
    progress_callback=None,
):
    """
    Scan all F&O Stocks.

    Returns
    -------
    DataFrame
    """

    symbols = get_nse_symbols()

    total = len(symbols)

    results = []

    for i, symbol in enumerate(symbols):

        if progress_callback:

            progress_callback(

                current=i + 1,

                total=total,

                symbol=symbol,

            )

        result = scan_symbol(

            symbol,

            period,

            interval,

            ma_period,

        )

        if result:

            results.append(result)

    results = pd.DataFrame(results)

    if not results.empty:

        results = results.sort_values(

            "Trend Since",

            ascending=False,

        ).reset_index(drop=True)

    return results
