# streamlit_app.py

import streamlit as st
from chatbot import get_chatbot_response
from database import (
    init_db, register_user, login_user,
    add_stock_to_db, remove_stock_from_db,
    get_user_portfolio
)
import random
import matplotlib.pyplot as plt

# Initialize database
init_db()

st.set_page_config(page_title="📈 Smart Stock Sentiment", layout="wide")

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- LOGIN & SIGNUP UI ---
if not st.session_state.logged_in:
    st.title("🔐 Login / Signup")
    tab1, tab2 = st.tabs(["Login", "Sign Up"])

    with tab1:
        user = st.text_input("Username", key="login_user")
        pwd = st.text_input("Password", type="password", key="login_pwd")
        if st.button("Login"):
            if login_user(user, pwd):
                st.session_state.logged_in = True
                st.session_state.username = user
                st.success(f"Welcome back, {user}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    with tab2:
        new_user = st.text_input("Create Username", key="new_user")
        new_pwd = st.text_input("Create Password", type="password", key="new_pwd")
        if st.button("Register"):
            if register_user(new_user, new_pwd):
                st.success("Registration successful. Please log in.")
            else:
                st.error("Username already exists.")

else:
    st.sidebar.success(f"👋 Logged in as: {st.session_state.username}")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("📊 Smart Stock Dashboard")
    st.caption("AI-powered insights, alerts, and portfolio management")

    # --- FLOATING CHAT ICON ---
    st.markdown("""
        <style>
        .chat-icon {
            position: fixed;
            bottom: 20px;
            right: 30px;
            background-color: #4CAF50;
            color: white;
            padding: 15px;
            border-radius: 50%;
            font-size: 22px;
            z-index: 100;
            cursor: pointer;
        }
        </style>
        <div onclick="window.scrollTo(0, document.body.scrollHeight);" class="chat-icon">💬</div>
    """, unsafe_allow_html=True)

    # --- MAIN TABS ---
    tab1, tab2, tab3, tab4 = st.tabs(["📁 Portfolio", "🚨 Alerts", "🤖 Chatbot", "📈 Sentiment Analyzer"])

    # --- PORTFOLIO ---
    with tab1:
        st.subheader("📁 Manage Your Portfolio")
        stock = st.text_input("Enter Stock Symbol (e.g. TSLA)", key="add_stock_input")
        col1, col2 = st.columns(2)
        if col1.button("➕ Add Stock"):
            add_stock_to_db(st.session_state.username, stock)
            st.success(f"{stock.upper()} added!")
        if col2.button("➖ Remove Stock"):
            remove_stock_from_db(st.session_state.username, stock)
            st.warning(f"{stock.upper()} removed!")

        st.subheader("📃 Your Current Portfolio")
        portfolio = get_user_portfolio(st.session_state.username)
        if portfolio:
            st.write(", ".join(portfolio))
        else:
            st.info("Your portfolio is empty.")

    # --- ALERT SYSTEM ---
    with tab2:
        st.subheader("🚨 Sentiment Alerts")
        st.markdown("**❗Disclaimer: This tool is for educational purposes. Please consult a financial advisor before making real investments.**", unsafe_allow_html=True)

        # Simulate sentiment
        sentiment_data = {s: random.choice(["positive", "neutral", "negative"]) for s in get_user_portfolio(st.session_state.username)}
        alerts = [f"⚠️ {s} has negative sentiment!" for s, val in sentiment_data.items() if val == "negative"]

        if alerts:
            for alert in alerts:
                st.error(alert)
        else:
            st.success("✅ All your stocks have stable sentiment.")

        st.subheader("📈 Sentiment Chart")
        if sentiment_data:
            scores = [1 if v == "positive" else 0 if v == "neutral" else -1 for v in sentiment_data.values()]
            fig, ax = plt.subplots()
            ax.bar(sentiment_data.keys(), scores, color=["green" if s == 1 else "orange" if s == 0 else "red" for s in scores])
            ax.axhline(0, color='gray')
            ax.set_ylabel("Sentiment")
            ax.set_title("Sentiment Analysis")
            st.pyplot(fig)

    # --- AI CHATBOT ---
    with tab3:
        st.subheader("💬 Ask the AI Chatbot", anchor="💬-ask-the-ai-chatbot")
        user_query = st.text_input("Type your stock-related question here", key="chat_input")
        if user_query:
            reply = get_chatbot_response(user_query)
            st.session_state.messages.append((user_query, reply))

        for q, r in reversed(st.session_state.messages[-5:]):
            st.markdown(f"🧑 You:** {q}")
            st.markdown(f"🤖 AI:** {r}")
        

    # --- ONBOARDING TOUR ---
    with st.expander("🧭 New User Tour"):
        st.info("🔹 Use the **Portfolio** tab to track your stocks.\n"
                "🔹 Get real-time **Alerts** on stock risks.\n"
                "🔹 Ask our AI bot for investment suggestions.\n"
                "🔹 Your data is saved securely.")



    # --- SENTIMENT ANALYZER ---
    with tab4:
        st.subheader("📈 Stock Sentiment Analyzer with News + Twitter + AI Logic")

        username = st.session_state.username

        if f"watchlist_{username}" not in st.session_state:
            st.session_state[f"watchlist_{username}"] = ["Tesla", "Apple"]

        watchlist = st.session_state[f"watchlist_{username}"]

        st.sidebar.subheader("➕ Add to Watchlist")
        new_stock = st.sidebar.text_input("Enter company/stock name:")
        if st.sidebar.button("Add Stock"):
            if new_stock and new_stock not in watchlist:
                watchlist.append(new_stock)

        from sentiment_news import fetch_google_news, get_sentiment, generate_wordcloud
        from twitter_sentiment import get_tweet_sentiment
        from recommender import make_recommendation
        import plotly.graph_objects as go
        from datetime import datetime

        for stock in watchlist:
            st.markdown(f"## 📊 {stock} — {datetime.now().strftime('%H:%M:%S')}")

            articles = fetch_google_news(stock)
            news_sentiment, _ = get_sentiment(articles)

            tweet_sentiment, tweets = get_tweet_sentiment(stock)
            if tweet_sentiment:
                combined = {
                    "neg": (news_sentiment["neg"] + tweet_sentiment["neg"]) / 2,
                    "neu": (news_sentiment["neu"] + tweet_sentiment["neu"]) / 2,
                    "pos": (news_sentiment["pos"] + tweet_sentiment["pos"]) / 2,
                    "compound": (news_sentiment["compound"] + tweet_sentiment["compound"]) / 2
                }
            else:
                combined = news_sentiment

            wc_img = generate_wordcloud(articles + tweets if tweets else articles)
            rec = make_recommendation(combined["compound"])

            if rec == "🔼 Strong Buy":
                st.success(f"📢 ALERT: {stock} is marked as Strong Buy!")

            col1, col2 = st.columns([2, 1])
            with col1:
                chart = go.Figure(data=[
                    go.Bar(name="Positive", x=["Sentiment"], y=[combined["pos"]], marker_color="green"),
                    go.Bar(name="Neutral", x=["Sentiment"], y=[combined["neu"]], marker_color="gray"),
                    go.Bar(name="Negative", x=["Sentiment"], y=[combined["neg"]], marker_color="red")
                ])
                chart.update_layout(barmode='group', height=300, title="Combined Sentiment Chart")
                st.plotly_chart(chart, use_container_width=True)

            with col2:
                st.image(wc_img, caption="Word Cloud (News + Tweets)")
                st.info(f"💡 Recommendation: *{rec}*")

            with st.expander("🧠 LLM-Based Prediction (Experimental)"):
                st.info("📌 This is an early-stage prediction using sentiment trends only.")
                if combined["compound"] > 0.2:
                    st.success("📈 Our model predicts a short-term positive trend.")
                elif combined["compound"] < -0.2:
                    st.error("📉 Our model predicts a possible downward trend.")
                else:
                    st.warning("⏳ Market seems uncertain. Hold for clarity.")

            st.markdown("---")
