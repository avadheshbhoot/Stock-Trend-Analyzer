"""
data_fetcher.py
Download market data and NSE F&O symbols.
"""

import pandas as pd
import requests
import yfinance as yf
from io import StringIO


def get_stock_data(
    ticker: str,
    period: str,
    interval: str,
) -> pd.DataFrame:
    """
    Download OHLC data from Yahoo Finance.
    """

    df = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if df.empty:
        raise ValueError(f"No data found for {ticker}")

    df.columns = df.columns.get_level_values(0)
    df.reset_index(inplace=True)

    df["Datetime"] = df["Datetime"].dt.tz_convert("Asia/Kolkata")
    df["Datetime"] = pd.to_datetime(df["Datetime"])

    df.rename(columns={"Datetime": "Date"}, inplace=True)

    if "Volume" in df.columns:
        df.drop(columns=["Volume"], inplace=True)

    df.set_index("Date", inplace=True)

    return df


def resample_ohlc(df: pd.DataFrame, timeframe: str) -> pd.DataFrame:
    """Resample OHLC data."""

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


def get_nse_symbols():
    """
    Fetch latest NSE F&O stock symbols.
    Returns:
        list[str]
    """

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/137.0 Safari/537.36"
        )
    }

    session = requests.Session()

    session.get(
        "https://www.nseindia.com",
        headers=headers,
        timeout=20,
    )

    url = "https://nsearchives.nseindia.com/content/fo/fo_mktlots.csv"

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

    stocks = [f"{x}.NS" for x in stocks]

    remove_list = {
        "SYMBOL.NS",
        "Symbol.NS",
        "NIFTY.NS",
        "BANKNIFTY.NS",
        "FINNIFTY.NS",
        "MIDCPNIFTY.NS",
        "NIFTYNXT50.NS",
    }

    stocks = [x for x in stocks if x not in remove_list]

    stocks = sorted(set(stocks))

    return stocks


def save_results(
    df: pd.DataFrame,
    output_file: str,
):
    """Save scan results."""

    df.to_excel(
        output_file,
        index=False,
    )
