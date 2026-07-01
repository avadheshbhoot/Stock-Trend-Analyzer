"""
trend_analyzer.py
Core trend analysis logic for the Stock Trend Analyzer project.
"""

from datetime import date, timedelta
import numpy as np
import pandas as pd
import talib

from config import (
    DEFAULT_PERIOD,
    DEFAULT_INTERVAL,
    RSI_PERIOD,
    ADX_PERIOD,
    RSI_UPTREND,
    RSI_DOWNTREND,
    ADX_THRESHOLD,
)

from data_fetcher import (
    get_stock_data,
    resample_ohlc,
)


def calculate_indicators(df: pd.DataFrame, ma: int) -> pd.DataFrame:
    """Calculate EMA, RSI and ADX."""

    df[f"EMA_{ma}_15min"] = (
        df["Close"].ewm(span=ma, adjust=False).mean().round(2)
    )

    for tf in ["45min", "90min", "180min"]:
        resampled = resample_ohlc(df, tf)
        ema_col = f"EMA_{ma}_{tf}"

        resampled[ema_col] = (
            resampled["Close"]
            .ewm(span=ma, adjust=False)
            .mean()
            .round(2)
        )

        df = df.join(resampled[[ema_col]], how="left")

    ema_cols = [
        f"EMA_{ma}_15min",
        f"EMA_{ma}_45min",
        f"EMA_{ma}_90min",
        f"EMA_{ma}_180min",
    ]

    df[ema_cols] = df[ema_cols].ffill()

    df["RSI"] = talib.RSI(
        df["Close"],
        timeperiod=RSI_PERIOD,
    ).round(2)

    df["ADX"] = talib.ADX(
        df["High"],
        df["Low"],
        df["Close"],
        timeperiod=ADX_PERIOD,
    ).round(2)

    return df


def calculate_trend(df: pd.DataFrame, ma: int) -> pd.DataFrame:
    """Calculate multi-timeframe trend."""

    for tf in ["15min", "45min", "90min", "180min"]:

        ema = f"EMA_{ma}_{tf}"

        trend = f"{tf}_trend"

        df[trend] = np.where(
            df["Close"] >= df[ema],
            "up_trend",
            "down_trend",
        )

    df["rsi_n_adx_trend"] = "-"

    up = (
        (df["RSI"] >= RSI_UPTREND)
        &
        (df["ADX"] >= ADX_THRESHOLD)
    )

    down = (
        (df["RSI"] <= RSI_DOWNTREND)
        &
        (df["ADX"] <= ADX_THRESHOLD)
    )

    df.loc[up, "rsi_n_adx_trend"] = "up_trend"
    df.loc[down, "rsi_n_adx_trend"] = "down_trend"

    df["main_trend"] = np.where(
        (df["15min_trend"] == df["45min_trend"])
        &
        (df["45min_trend"] == df["90min_trend"])
        &
        (df["90min_trend"] == df["180min_trend"]),
        df["15min_trend"],
        "-",
    )

    condition = (
        (df["main_trend"] == df["main_trend"].shift(1))
        &
        (df["main_trend"].shift(1) == df["main_trend"].shift(2))
        &
        (df["main_trend"].shift(2) == df["main_trend"].shift(3))
        &
        (df["rsi_n_adx_trend"] == df["rsi_n_adx_trend"].shift(1))
    )

    df["safe_trend"] = "-"
    df.loc[condition, "safe_trend"] = df["main_trend"]

    return df


def trend_start(df: pd.DataFrame):
    """Return trend start timestamp and candle count."""

    last = df["safe_trend"].iloc[-1]

    count = 0

    for value in reversed(df["safe_trend"].tolist()):
        if value == last:
            count += 1
        else:
            break

    start_index = len(df) - count

    return df.index[start_index], count


def analyze_stock(
    ticker: str,
    ma: int,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
):
    """Analyze one stock."""

    df = get_stock_data(
        ticker=ticker,
        period=period,
        interval=interval,
    )

    df = calculate_indicators(df, ma)
    df = calculate_trend(df, ma)

    trend_date, candles = trend_start(df)

    return df, trend_date, candles


def scan_market(
    tickers,
    ma: int,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
):
    """Analyze multiple stocks."""

    rows = []

    for ticker in tickers:

        try:

            df, trend_date, candles = analyze_stock(
                ticker,
                ma,
                period,
                interval,
            )

            rows.append(
                {
                    "Ticker": ticker,
                    "Trend": df["safe_trend"].iloc[-1],
                    "Trend Start": trend_date,
                    "Trend Date": trend_date.date(),
                    "Candles": candles,
                    "Close": round(df["Close"].iloc[-1], 2),
                    "RSI": round(df["RSI"].iloc[-1], 2),
                    "ADX": round(df["ADX"].iloc[-1], 2),
                }
            )

        except Exception as ex:

            rows.append(
                {
                    "Ticker": ticker,
                    "Trend": "ERROR",
                    "Error": str(ex),
                }
            )

    return pd.DataFrame(rows)


def filter_n_days_trend(df_results: pd.DataFrame, n_days: int):
    """Return stocks whose trend started N business days ago."""

    target = date.today()

    count = 0

    while count < n_days:
        target -= timedelta(days=1)
        if target.weekday() < 5:
            count += 1

    return (
        df_results[
            df_results["Trend Date"] == target
        ]
        .sort_values(
            by=["Trend", "Trend Start"]
        )
        .reset_index(drop=True)
    )


def get_market_trend(
    ma: int,
    period: str = DEFAULT_PERIOD,
    interval: str = DEFAULT_INTERVAL,
):

    df, _, _ = analyze_stock(
        "^NSEI",
        ma,
        period,
        interval,
    )

    return df["safe_trend"].iloc[-1]
