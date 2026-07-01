"""
data_fetcher.py
Download market data and NSE F&O symbols.
"""

from functools import lru_cache
from io import StringIO
import time

import pandas as pd
import requests
import yfinance as yf


# ==========================================================
# Symbol Utilities
# ==========================================================

def validate_symbol(symbol: str) -> str:
    """
    Convert user input to Yahoo Finance NSE symbol.

    Examples
    --------
    reliance -> RELIANCE.NS
    RELIANCE -> RELIANCE.NS
    RELIANCE.NS -> RELIANCE.NS
    """

    symbol = symbol.strip().upper()

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    return symbol


# ==========================================================
# Market Data
# ==========================================================

def get_stock_data(
    ticker: str,
    period: str,
    interval: str,
    auto_adjust: bool = True,
    retries: int = 3,
) -> pd.DataFrame:
    """
    Download OHLC data from Yahoo Finance.

    Returns
    -------
    DataFrame indexed by Date.
    """

    ticker = validate_symbol(ticker)

    last_error = None

    for attempt in range(retries):

        try:

            df = yf.download(
                ticker=ticker,
                period=period,
                interval=interval,
                auto_adjust=auto_adjust,
                progress=False,
                threads=False,
            )

            if df.empty:
                raise ValueError(f"No data found for {ticker}")

            # Remove MultiIndex if present
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)

            df.reset_index(inplace=True)

            # Yahoo returns Date for daily and Datetime for intraday
            date_col = "Datetime" if "Datetime" in df.columns else "Date"

            df.rename(columns={date_col: "Date"}, inplace=True)

            # Convert timezone only if timezone-aware
            if pd.api.types.is_datetime64tz_dtype(df["Date"]):
                df["Date"] = df["Date"].dt.tz_convert("Asia/Kolkata")

            df["Date"] = pd.to_datetime(df["Date"])

            if "Volume" in df.columns:
                df.drop(columns=["Volume"], inplace=True)

            df.set_index("Date", inplace=True)

            df = df[~df.index.duplicated(keep="last")]

            df.sort_index(inplace=True)

            return df

        except Exception as e:

            last_error = e

            if attempt < retries - 1:
                time.sleep(1)

    raise RuntimeError(last_error)


# ==========================================================
# Indicators
# ==========================================================

def add_moving_average(
    df: pd.DataFrame,
    period: int,
) -> pd.DataFrame:
    """
    Add Simple Moving Average column.
    """

    df = df.copy()

    df[f"MA_{period}"] = (
        df["Close"]
        .rolling(period)
        .mean()
    )

    return df


# ==========================================================
# Resampling
# ==========================================================

def resample_ohlc(
    df: pd.DataFrame,
    timeframe: str,
) -> pd.DataFrame:
    """
    Resample OHLC data.
    """

    if df.empty:
        return df

    return (
        df.resample(timeframe)
        .agg(
            {
                "Open": "first",
                "High": "max",
                "Low": "min",
                "Close": "last",
            }
        )
        .dropna()
    )


# ==========================================================
# NSE F&O Symbols
# ==========================================================

@lru_cache(maxsize=1)
def get_nse_symbols() -> list[str]:
    """
    Fetch latest NSE F&O symbols.

    Cached during application lifetime.
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "Chrome/137.0 Safari/537.36"
        )
    }

    session = requests.Session()

    session.get(
        "https://www.nseindia.com",
        headers=headers,
        timeout=20,
    )

    url = (
        "https://nsearchives.nseindia.com/"
        "content/fo/fo_mktlots.csv"
    )

    response = session.get(
        url,
        headers=headers,
        timeout=20,
    )

    response.raise_for_status()

    df = pd.read_csv(StringIO(response.text))

    df.columns = df.columns.str.strip()

    stocks = (
        df["SYMBOL"]
        .astype(str)
        .str.strip()
        .tolist()
    )

    remove_list = {
        "SYMBOL",
        "Symbol",
        "NIFTY",
        "BANKNIFTY",
        "FINNIFTY",
        "MIDCPNIFTY",
        "NIFTYNXT50",
    }

    stocks = [
        validate_symbol(x)
        for x in stocks
        if x not in remove_list
    ]

    stocks = sorted(set(stocks))

    return stocks


# ==========================================================
# Save Results
# ==========================================================

def save_results(
    df: pd.DataFrame,
    output_file: str,
):
    """
    Save scan results.

    Supports:
        *.xlsx
        *.csv
    """

    if output_file.lower().endswith(".xlsx"):

        df.to_excel(
            output_file,
            index=False,
        )

    elif output_file.lower().endswith(".csv"):

        df.to_csv(
            output_file,
            index=False,
        )

    else:

        raise ValueError(
            "Output file must be .xlsx or .csv"
        )
