import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="ربات اسکنر بازار", page_icon="📈", layout="wide")

st.title("📈 ربات اسکنر چند بازاری")
st.caption("نسخه ساده | حالت آزمایشی (Dry-Run)")

# تنظیمات
pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT"]

# اتصال به بایننس (بدون نیاز به API Key برای دیدن قیمت)
exchange = ccxt.binance()

# سایدبار تنظیمات
st.sidebar.header("تنظیمات")
threshold = st.sidebar.slider("آستانه انحراف قیمت (%)", 0.3, 3.0, 0.8, 0.1)
refresh_rate = st.sidebar.slider("هر چند ثانیه یکبار به‌روز شود", 5, 30, 10)

# دکمه شروع
if "running" not in st.session_state:
    st.session_state.running = False

col1, col2 = st.columns(2)
with col1:
    if st.button("▶ شروع اسکن", use_container_width=True):
        st.session_state.running = True
with col2:
    if st.button("⏹ توقف", use_container_width=True):
        st.session_state.running = False

status = "🟢 در حال اجرا" if st.session_state.running else "🔴 متوقف"
st.subheader(f"وضعیت: {status}")

# محل نمایش داده‌ها
price_placeholder = st.empty()
opportunity_placeholder = st.empty()
log_placeholder = st.empty()

def get_prices():
    data = []
    for pair in pairs:
        try:
            ticker = exchange.fetch_ticker(pair)
            data.append({
                "جفت‌ارز": pair,
                "قیمت": ticker['last'],
                "تغییر ۲۴ساعته (%)": round(ticker['percentage'], 2) if ticker['percentage'] else 0,
                "حجم": round(ticker['quoteVolume'] / 1000000, 2) if ticker['quoteVolume'] else 0
            })
        except:
            continue
    return pd.DataFrame(data)

# حلقه اصلی
if st.session_state.running:
    while st.session_state.running:
        df = get_prices()
        
        with price_placeholder.container():
            st.subheader("قیمت‌های زنده")
            st.dataframe(df, use_container_width=True)
        
        # پیدا کردن فرصت ساده (تغییر زیاد)
        opportunities = df[abs(df["تغییر ۲۴ساعته (%)"]) >= threshold]
        
        with opportunity_placeholder.container():
            st.subheader("فرصت‌های پیدا شده")
            if not opportunities.empty:
                st.dataframe(opportunities, use_container_width=True)
                st.success(f"{len(opportunities)} فرصت پیدا شد")
            else:
                st.info("فعلاً فرصتی با آستانه تعیین‌شده پیدا نشد")
        
        with log_placeholder.container():
            st.caption(f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")
        
        time.sleep(refresh_rate)
        st.rerun()
else:
    st.info("برای شروع، دکمه «شروع اسکن» را بزنید.")
