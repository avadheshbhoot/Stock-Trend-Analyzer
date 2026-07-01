"""
indicators.py

Technical Indicators
"""

import numpy as np
import pandas as pd


# ==========================================================
# Simple Moving Average
# ==========================================================

def sma(
    df: pd.DataFrame,
    period: int,
    column: str = "Close",
) -> pd.DataFrame:
    """
    Add Simple Moving Average.
    """

    df = df.copy()

    df[f"SMA_{period}"] = (
        df[column]
        .rolling(period)
        .mean()
    )

    return df


# ==========================================================
# Exponential Moving Average
# ==========================================================

def ema(
    df: pd.DataFrame,
    period: int,
    column: str = "Close",
) -> pd.DataFrame:
    """
    Add Exponential Moving Average.
    """

    df = df.copy()

    df[f"EMA_{period}"] = (
        df[column]
        .ewm(
            span=period,
            adjust=False,
        )
        .mean()
    )

    return df


# ==========================================================
# RSI
# ==========================================================

def rsi(
    df: pd.DataFrame,
    period: int = 14,
    column: str = "Close",
) -> pd.DataFrame:

    df = df.copy()

    delta = df[column].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()

    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    df["RSI"] = 100 - (100 / (1 + rs))

    return df


# ==========================================================
# ATR
# ==========================================================

def atr(
    df: pd.DataFrame,
    period: int = 14,
) -> pd.DataFrame:

    df = df.copy()

    high_low = df["High"] - df["Low"]

    high_close = np.abs(
        df["High"] - df["Close"].shift()
    )

    low_close = np.abs(
        df["Low"] - df["Close"].shift()
    )

    ranges = pd.concat(

        [

            high_low,

            high_close,

            low_close,

        ],

        axis=1,

    )

    tr = ranges.max(axis=1)

    df["ATR"] = tr.rolling(period).mean()

    return df


# ==========================================================
# MACD
# ==========================================================

def macd(
    df: pd.DataFrame,
    fast: int = 12,
    slow: int = 26,
    signal: int = 9,
) -> pd.DataFrame:

    df = df.copy()

    ema_fast = (
        df["Close"]
        .ewm(
            span=fast,
            adjust=False,
        )
        .mean()
    )

    ema_slow = (
        df["Close"]
        .ewm(
            span=slow,
            adjust=False,
        )
        .mean()
    )

    df["MACD"] = ema_fast - ema_slow

    df["MACD Signal"] = (
        df["MACD"]
        .ewm(
            span=signal,
            adjust=False,
        )
        .mean()
    )

    df["MACD Histogram"] = (
        df["MACD"] - df["MACD Signal"]
    )

    return df


# ==========================================================
# Bollinger Bands
# ==========================================================

def bollinger(
    df: pd.DataFrame,
    period: int = 20,
    std: int = 2,
) -> pd.DataFrame:

    df = df.copy()

    sma_value = (
        df["Close"]
        .rolling(period)
        .mean()
    )

    std_value = (
        df["Close"]
        .rolling(period)
        .std()
    )

    df["BB Upper"] = sma_value + std * std_value

    df["BB Middle"] = sma_value

    df["BB Lower"] = sma_value - std * std_value

    return df


# ==========================================================
# Trend
# ==========================================================

def price_vs_sma(
    df: pd.DataFrame,
    period: int,
):
    """
    Returns:

    Up Trend

    Down Trend
    """

    sma_col = f"SMA_{period}"

    if sma_col not in df.columns:

        df = sma(

            df,

            period,

        )

    last = df.iloc[-1]

    if last["Close"] > last[sma_col]:

        return "Up Trend"

    return "Down Trend"
