"""
Functions related to downloading market data.
"""

import pandas as pd
import yfinance as yf


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

    df.columns = [
        col for col in df.columns.get_level_values(0)
    ]

    df.reset_index(inplace=True)

    df["Datetime"] = (
        df["Datetime"]
        .dt.tz_convert("Asia/Kolkata")
    )

    df["Datetime"] = pd.to_datetime(
        df["Datetime"]
    )

    df.rename(
        columns={
            "Datetime": "Date"
        },
        inplace=True,
    )

    if "Volume" in df.columns:
        df.drop(
            columns="Volume",
            inplace=True,
        )

    df.set_index("Date", inplace=True)

    return df


def resample_ohlc(
    df: pd.DataFrame,
    timeframe: str,
) -> pd.DataFrame:
    """
    Resample OHLC data.
    """

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


def load_symbols(csv_path: str):
    """
    Load NSE symbols from CSV.
    """

    symbols = pd.read_csv(csv_path)

    if "Symbol" not in symbols.columns:
        raise ValueError(
            "CSV must contain Symbol column."
        )

    return (
        symbols["Symbol"]
        .dropna()
        .tolist()
    )


def save_results(
    df: pd.DataFrame,
    output_file: str,
):
    """
    Save output dataframe.
    """

    df.to_excel(
        output_file,
        index=False,
    )
    