# Stock Trend Analyzer

A Streamlit application that scans NSE stocks using live Yahoo Finance
data and identifies multi-timeframe trends.

## Features

-   Scan all NSE stocks
-   Analyze a single stock
-   User-selectable EMA period (default: 50)
-   Multi-timeframe EMA analysis (15m, 45m, 90m, 180m)
-   RSI and ADX confirmation
-   Interactive Plotly charts
-   Export scan results to Excel

## Project Structure

    Stock-Trend-Analyzer/
    │
    ├── app.py
    ├── config.py
    ├── data_fetcher.py
    ├── trend_analyzer.py
    ├── charts.py
    ├── requirements.txt
    ├── data/
    │   └── nse_symbols.csv

## Installation

``` bash
pip install -r requirements.txt
```

## Run

``` bash
streamlit run app.py
```

## Technologies

-   Python
-   Streamlit
-   Pandas
-   NumPy
-   Plotly
-   yfinance
-   TA-Lib

## Future Improvements

-   Automatic NSE symbol updates
-   Watchlist support
-   Portfolio tracking
-   Additional indicators
-   Deployment on Streamlit Community Cloud
