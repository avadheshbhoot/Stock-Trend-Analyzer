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

        from trend import trend_summary

        trend = trend_summary(
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
