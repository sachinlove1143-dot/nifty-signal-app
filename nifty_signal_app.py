import streamlit as st
import yfinance as yf
import pandas as pd
import datetime

# Set up Streamlit page
st.set_page_config(page_title="📈 NIFTY / BANKNIFTY / FINNIFTY Signals", layout="centered")
st.title("💹 Intraday Signal Generator")
st.markdown("Strategy: **RSI + EMA** with Alerts and Charts")

# Dropdown options
symbol_map = {
    "NIFTY 50": "^NSEI",
    "BANK NIFTY": "^NSEBANK",
    "FINNIFTY": "NSE:FINNIFTY"
}

option = st.selectbox("Select Index:", list(symbol_map.keys()))

# RSI calculation function
def compute_rsi(series, period=14):
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(window=period).mean()
    loss = (-delta.clip(upper=0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# Flatten columns if MultiIndex
def flatten_columns(df):
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    return df

# Signal logic
if st.button("Get Signal"):
    symbol = symbol_map[option]

    try:
        df = yf.download(tickers=symbol, period="5d", interval="15m", progress=False)
        df.dropna(inplace=True)

        # Calculate RSI and EMA manually
        df['RSI'] = compute_rsi(df['Close'], 14)
        df['EMA'] = df['Close'].ewm(span=20, adjust=False).mean()
        df.dropna(inplace=True)

        latest = df.iloc[-1]

        # Use float() to avoid errors
        close = float(latest['Close'])
        rsi = float(latest['RSI'])
        ema = float(latest['EMA'])

        # Enhanced strategy logic (RSI + EMA + Trend direction)
        trend = df['EMA'].iloc[-1] - df['EMA'].iloc[-5]

        if rsi < 30 and close > ema and trend > 0:
            signal = "✅ BUY Signal"
            alert = "🔔 Consider entering long position."
        elif rsi > 70 and close < ema and trend < 0:
            signal = "❌ SELL Signal"
            alert = "🔔 Consider exiting or shorting."
        else:
            signal = "⚠️ HOLD / No clear signal"
            alert = "🕒 Wait for better conditions."

        # Output
        st.subheader(f"{option} - {signal}")
        st.metric("Price", f"₹{close:.2f}")
        st.metric("RSI", f"{rsi:.2f}")
        st.metric("EMA", f"{ema:.2f}")
        st.success(alert)

        # Fix MultiIndex before charts
        df = flatten_columns(df)

        # Show chart
        st.line_chart(df[['Close', 'EMA']])
        st.line_chart(df[['RSI']])

        # Timestamp
        st.caption(f"Last updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    except Exception as e:
        st.error(f"❌ Error: {e}")
