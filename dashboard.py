import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import random
from dotenv import load_dotenv
from supabase import create_client, Client
from streamlit_autorefresh import st_autorefresh
from analysis import (
    get_top_gainers,
    get_average_market_cap,
    get_total_market_value,
    get_volatility_ranking
)

load_dotenv()

supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

st.set_page_config(
    page_title="CryptoSphere Analytics",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st_autorefresh(interval=60000)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;800&display=swap');

* { font-family: 'Syne', sans-serif; }
code, .mono { font-family: 'Space Mono', monospace; }

html, body, [data-testid="stAppViewContainer"] {
    background: #060b14;
    color: #e2e8f0;
}

[data-testid="stAppViewContainer"] {
    background: radial-gradient(ellipse at 20% 20%, #0d1f3c 0%, #060b14 50%, #0a0f1e 100%);
}

[data-testid="stHeader"] { background: transparent; }

.hero-title {
    font-family: 'Syne', sans-serif;
    font-weight: 800;
    font-size: 3.2rem;
    background: linear-gradient(135deg, #00f5ff, #0080ff, #7c3aed);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    letter-spacing: -1px;
    margin-bottom: 0;
}

.hero-sub {
    text-align: center;
    color: #4a6fa5;
    font-size: 0.95rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-top: 4px;
}

.kpi-card {
    background: linear-gradient(135deg, #0d1f3c 0%, #111827 100%);
    border: 1px solid #1e3a5f;
    border-radius: 16px;
    padding: 24px 20px;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.kpi-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #00f5ff, #0080ff, #7c3aed);
}

.kpi-label {
    color: #4a6fa5;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 8px;
}

.kpi-value {
    font-family: 'Space Mono', monospace;
    font-size: 1.8rem;
    font-weight: 700;
    color: #00f5ff;
}

.kpi-delta-up { color: #00ff88; font-size: 0.85rem; }
.kpi-delta-down { color: #ff4466; font-size: 0.85rem; }

.section-title {
    font-weight: 800;
    font-size: 1.1rem;
    color: #94a3b8;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 12px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.divider {
    border: none;
    border-top: 1px solid #1e3a5f;
    margin: 28px 0;
}

.ticker-row {
    display: flex;
    gap: 32px;
    overflow: hidden;
    padding: 10px 0;
    border-top: 1px solid #1e3a5f;
    border-bottom: 1px solid #1e3a5f;
    margin-bottom: 24px;
}

.ticker-item {
    white-space: nowrap;
    font-family: 'Space Mono', monospace;
    font-size: 0.8rem;
    color: #4a6fa5;
}
</style>
""", unsafe_allow_html=True)


def load_all_data():
    response = supabase.table("crypto_market")\
        .select("*")\
        .order("market_cap_rank")\
        .execute()
    return pd.DataFrame(response.data)


def make_candlestick(df, coin_name):
    price = df[df["name"] == coin_name]["current_price"].values
    if len(price) == 0:
        return None
    base = float(price[0])
    dates = pd.date_range(end=pd.Timestamp.now(), periods=40, freq="h")
    opens, highs, lows, closes = [], [], [], []
    current = base * 0.92
    for _ in dates:
        o = current
        c = o * (1 + random.uniform(-0.025, 0.025))
        h = max(o, c) * (1 + random.uniform(0.002, 0.012))
        l = min(o, c) * (1 - random.uniform(0.002, 0.012))
        opens.append(o)
        closes.append(c)
        highs.append(h)
        lows.append(l)
        current = c
    return dates, opens, highs, lows, closes


df = load_all_data()
total_market = get_total_market_value()
avg_market_cap = get_average_market_cap()
top_gainers = get_top_gainers()
most_volatile = get_volatility_ranking()
highest_gainer = top_gainers[0] if top_gainers else {}
most_volatile_coin = most_volatile[0] if most_volatile else {}

st.markdown('<div class="hero-title">💎 CryptoSphere</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Real-Time Market Intelligence Platform</div>', unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if not df.empty:
    ticker_html = '<div class="ticker-row">'
    for _, row in df.head(10).iterrows():
        change = row["price_change_24h"]
        color = "#00ff88" if change >= 0 else "#ff4466"
        arrow = "▲" if change >= 0 else "▼"
        ticker_html += f'<div class="ticker-item">{row["symbol"].upper()} <span style="color:{color}">{arrow} ${row["current_price"]:,.2f}</span></div>'
    ticker_html += '</div>'
    st.markdown(ticker_html, unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">💰 Total Market Cap</div>
        <div class="kpi-value">${total_market/1e12:.2f}T</div>
    </div>""", unsafe_allow_html=True)

with col2:
    gainer_name = highest_gainer.get("name", "N/A")
    gainer_val = highest_gainer.get("price_change_24h", 0)
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📈 Top Gainer 24h</div>
        <div class="kpi-value" style="font-size:1.3rem">{gainer_name}</div>
        <div class="kpi-delta-up">▲ {gainer_val:.2f}%</div>
    </div>""", unsafe_allow_html=True)

with col3:
    vol_name = most_volatile_coin.get("name", "N/A")
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">⚡ Most Volatile</div>
        <div class="kpi-value" style="font-size:1.3rem">{vol_name}</div>
    </div>""", unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">📊 Avg Market Cap</div>
        <div class="kpi-value">${avg_market_cap/1e9:.1f}B</div>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<hr class="divider">', unsafe_allow_html=True)

st.markdown('<div class="section-title">🕯 Candlestick Charts — Top Coins</div>', unsafe_allow_html=True)

top_coins = df.head(4)["name"].tolist()
cols = st.columns(2)

for i, coin in enumerate(top_coins):
    result = make_candlestick(df, coin)
    if result:
        dates, opens, highs, lows, closes = result
        fig = go.Figure(data=[go.Candlestick(
            x=dates,
            open=opens, high=highs,
            low=lows, close=closes,
            increasing=dict(
                line=dict(color="#00ff88", width=1),
                fillcolor="#00ff88"
            ),
            decreasing=dict(
                line=dict(color="#ff4466", width=1),
                fillcolor="#ff4466"
            )
        )])
        fig.update_layout(
            title=dict(text=f"{coin}", font=dict(color="#00f5ff", size=14)),
            paper_bgcolor="#0d1f3c",
            plot_bgcolor="#060b14",
            font_color="#4a6fa5",
            xaxis=dict(gridcolor="#1e3a5f", showgrid=True),
            yaxis=dict(gridcolor="#1e3a5f", showgrid=True),
            xaxis_rangeslider_visible=False,
            height=300,
            margin=dict(l=10, r=10, t=40, b=10)
        )
        with cols[i % 2]:
            st.plotly_chart(fig, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">🏆 Market Cap Leaders</div>', unsafe_allow_html=True)
    fig_bar = go.Figure(go.Bar(
        x=df.head(10)["name"],
        y=df.head(10)["market_cap"],
        marker=dict(
            color=df.head(10)["market_cap"],
            colorscale=[[0, "#0d1f3c"], [0.5, "#0080ff"], [1, "#00f5ff"]],
            line=dict(color="#00f5ff", width=0.5)
        )
    ))
    fig_bar.update_layout(
        paper_bgcolor="#0d1f3c",
        plot_bgcolor="#060b14",
        font_color="#4a6fa5",
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">📈 24h Price Change</div>', unsafe_allow_html=True)
    colors = ["#00ff88" if x > 0 else "#ff4466" for x in df["price_change_24h"]]
    fig_change = go.Figure(go.Bar(
        x=df["name"],
        y=df["price_change_24h"],
        marker_color=colors,
        marker_line_width=0
    ))
    fig_change.update_layout(
        paper_bgcolor="#0d1f3c",
        plot_bgcolor="#060b14",
        font_color="#4a6fa5",
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False
    )
    st.plotly_chart(fig_change, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-title">💧 Volume Comparison</div>', unsafe_allow_html=True)
    fig_vol = go.Figure(go.Bar(
        x=df.head(10)["name"],
        y=df.head(10)["total_volume"],
        marker=dict(
            color=df.head(10)["total_volume"],
            colorscale=[[0, "#1a0a2e"], [0.5, "#7c3aed"], [1, "#c084fc"]],
        )
    ))
    fig_vol.update_layout(
        paper_bgcolor="#0d1f3c",
        plot_bgcolor="#060b14",
        font_color="#4a6fa5",
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False
    )
    st.plotly_chart(fig_vol, use_container_width=True)

with col2:
    st.markdown('<div class="section-title">⚡ Volatility Ranking</div>', unsafe_allow_html=True)
    vol_df = pd.DataFrame(most_volatile)
    fig_vrank = go.Figure(go.Bar(
        x=vol_df["name"],
        y=vol_df["volatility_score"],
        marker=dict(
            color=vol_df["volatility_score"],
            colorscale=[[0, "#1a0505"], [0.5, "#ff4466"], [1, "#ff8800"]],
        )
    ))
    fig_vrank.update_layout(
        paper_bgcolor="#0d1f3c",
        plot_bgcolor="#060b14",
        font_color="#4a6fa5",
        xaxis=dict(gridcolor="#1e3a5f"),
        yaxis=dict(gridcolor="#1e3a5f"),
        height=320,
        margin=dict(l=10, r=10, t=20, b=10),
        showlegend=False
    )
    st.plotly_chart(fig_vrank, use_container_width=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Live Market Data</div>', unsafe_allow_html=True)

display_df = df[["name", "symbol", "current_price", "market_cap",
                  "total_volume", "price_change_24h", "volatility_score"]].copy()
display_df.columns = ["Name", "Symbol", "Price (USD)", "Market Cap",
                       "Volume", "24h Change %", "Volatility Score"]
display_df["Price (USD)"] = display_df["Price (USD)"].apply(lambda x: f"${x:,.2f}")
display_df["Market Cap"] = display_df["Market Cap"].apply(lambda x: f"${x:,.0f}")
display_df["Volume"] = display_df["Volume"].apply(lambda x: f"${x:,.0f}")
display_df["24h Change %"] = display_df["24h Change %"].apply(lambda x: f"{x:.2f}%")
display_df["Volatility Score"] = display_df["Volatility Score"].apply(lambda x: f"{x:,.0f}")

def color_row(row):
    try:
        num = float(row["24h Change %"].replace('%', ''))
        if num > 0:
            return ['background-color: rgba(0, 255, 136, 0.12); color: #00ff88' if col == "24h Change %" 
                    else 'background-color: rgba(0, 255, 136, 0.06)' for col in row.index]
        elif num < 0:
            return ['background-color: rgba(255, 68, 102, 0.12); color: #ff4466' if col == "24h Change %" 
                    else 'background-color: rgba(255, 68, 102, 0.06)' for col in row.index]
    except:
        pass
    return ['' for _ in row.index]

styled_df = display_df.style.apply(color_row, axis=1)
st.dataframe(styled_df, use_container_width=True, height=420)


st.markdown("<br>", unsafe_allow_html=True)
st.markdown('<p style="text-align:center; color:#1e3a5f; font-size:0.75rem; letter-spacing:2px;">CRYPTOSPHERE ANALYTICS • POWERED BY COINGECKO & SUPABASE</p>', unsafe_allow_html=True)
