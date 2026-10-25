import streamlit as st
import ccxt
import pandas as pd
from datetime import datetime
import time

st.set_page_config(page_title="ربات اسکنر بازار", page_icon="📈", layout="wide")

st.title("📈 ربات اسکنر چند بازاری")
st.caption("نسخه ساده | حالت آزمایشی (Dry-Run)")

# لیست جفت‌ارزها
pairs = ["BTC/USDT", "ETH/USDT", "SOL/USDT", "BNB/USDT", "XRP/USDT", 
         "ADA/USDT", "DOGE/USDT", "AVAX/USDT", "DOT/USDT", "LINK/USDT"]

# اتصال به بایننس
exchange = ccxt.binance({
    'enableRateLimit': True
})

# سایدبار تنظیمات
st.sidebar.header("تنظیمات")
threshold = st.sidebar.slider("آستانه تغییر ۲۴ساعته (%)", 0.5, 5.0, 1.5, 0.1)
refresh_rate = st.sidebar.slider("زمان به‌روزرسانی (ثانیه)", 5, 30, 10)

# وضعیت اجرا
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

price_placeholder = st.empty()
opportunity_placeholder = st.empty()
log_placeholder = st.empty()

def get_prices():
    data = []
    for pair in pairs:
        try:
            ticker = exchange.fetch_ticker(pair)
            change = ticker.get('percentage', 0) or 0
            data.append({
                "pair": pair,
                "price": ticker.get('last', 0),
                "change_24h": round(change, 2),
                "volume": round((ticker.get('quoteVolume') or 0) / 1_000_000, 2)
            })
        except Exception as e:
            continue
    return pd.DataFrame(data)

if st.session_state.running:
    df = get_prices()

    with price_placeholder.container():
        st.subheader("قیمت‌های زنده")
        if not df.empty:
            # نمایش با نام فارسی
            display_df = df.rename(columns={
                "pair": "جفت‌ارز",
                "price": "قیمت",
                "change_24h": "تغییر ۲۴ساعته (%)",
                "volume": "حجم (میلیون)"
            })
            st.dataframe(display_df, use_container_width=True)
        else:
            st.warning("در حال دریافت اطلاعات از بایننس... لطفاً چند لحظه صبر کنید.")

    with opportunity_placeholder.container():
        st.subheader("فرصت‌های پیدا شده")
        if not df.empty:
            opportunities = df[abs(df["change_24h"]) >= threshold]
            if not opportunities.empty:
                display_opp = opportunities.rename(columns={
                    "pair": "جفت‌ارز",
                    "price": "قیمت",
                    "change_24h": "تغییر ۲۴ساعته (%)",
                    "volume": "حجم (میلیون)"
                })
                st.dataframe(display_opp, use_container_width=True)
                st.success(f"{len(opportunities)} فرصت پیدا شد")
            else:
                st.info("فعلاً فرصتی با آستانه تعیین‌شده پیدا نشد")
        else:
            st.info("هنوز داده‌ای دریافت نشده")

    with log_placeholder.container():
        st.caption(f"آخرین به‌روزرسانی: {datetime.now().strftime('%H:%M:%S')}")

    time.sleep(refresh_rate)
    st.rerun()
else:
    st.info("برای شروع، دکمه «شروع اسکن» را بزنید.")
