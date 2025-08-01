import streamlit as st
import yfinance as yf
import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

st.set_page_config(page_title="📈 NIFTY / BANKNIFTY / FINNIFTY Signals", layout="centered")
st.title("💹 Intraday Signal Generator")
st.markdown("Strategy: RSI + EMA (15-min interval)")

symbol_map = {
    "NIFTY 50": "^NSEI",
    "BANKNIFTY": "^NSEBANK",
    "FINNIFTY": "NSE:FINNIFTY"
}

option = st.selectbox("Select Index:", list(symbol_map.keys()))

if st.button("🔍 Get Signal"):
    symbol = symbol_map[option]

    try:
        df = yf.download(tickers=symbol, period="5d", interval="15m", progress=False)
        df.dropna(inplace=True)

        df['RSI'] = RSIIndicator(df['Close']).rsi()
        df['EMA'] = EMAIndicator(df['Close'], window=20).ema_indicator()

        latest = df.iloc[-1]
        rsi_val = latest['RSI']
        ema_val = latest['EMA']
        close_val = latest['Close']

        # Generate signal
        if rsi_val < 30 and close_val > ema_val:
            signal = "✅ BUY Signal"
        elif rsi_val > 70 and close_val < ema_val:
            signal = "❌ SELL Signal"
        else:
            signal = "⚠️ HOLD / No clear signal"

        st.subheader(f"{option} - {signal}")
        st.metric("Price", f"₹{close_val:.2f}")
        st.metric("RSI", f"{rsi_val:.2f}")
        st.metric("EMA", f"{ema_val:.2f}")

        # Optional note
        if signal == "⚠️ HOLD / No clear signal":
            st.info("🕒 Wait for better conditions.")

    except Exception as e:
        st.error(f"❌ Error: {e}")
