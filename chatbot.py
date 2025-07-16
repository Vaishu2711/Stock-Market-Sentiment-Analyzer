import os
import re
import yfinance as yf
import google.generativeai as genai
from dotenv import load_dotenv

# Load API Key from .env
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Use the working Gemini model
model = genai.GenerativeModel("gemini-1.5-flash")

def extract_tickers_from_text(text):
    """
    Extract potential stock tickers (1-5 uppercase letters) from input.
    Validate them via yfinance (must have live price).
    """
    potential = re.findall(r"\b[A-Z]{1,5}\b", text.upper())
    valid_tickers = []
    for sym in set(potential):
        try:
            info = yf.Ticker(sym).fast_info
            if getattr(info, "last_price", None) is not None:
                valid_tickers.append(sym)
        except:
            continue
    return valid_tickers

def get_stock_summary(ticker):
    """
    Return real-time stock summary: price, last 5 days, short summary.
    """
    try:
        stock = yf.Ticker(ticker)
        fast = stock.fast_info
        hist = stock.history(period="5d")

        price = getattr(fast, "last_price", None)
        if price is None and not hist.empty:
            price = hist["Close"].iloc[-1]

        name = stock.info.get("shortName", ticker)
        summary = stock.info.get("longBusinessSummary", "Summary not available.")
        history = hist['Close'].tolist() if not hist.empty else "N/A"

        return f"""
📌 **{name} ({ticker})**
- Current Price: ${price}
- Last 5 Days: {history}
- Summary: {summary[:300]}...
"""
    except Exception as e:
        return f"⚠ Error fetching data for {ticker}: {e}"

def get_chatbot_response(user_query):
    """
    Generates an AI answer to the user's query using real stock data.
    """
    tickers = extract_tickers_from_text(user_query)
    context = "📊 Real-time stock data:\n\n"

    if tickers:
        for symbol in tickers:
            context += get_stock_summary(symbol) + "\n\n"
    else:
        context += "No recognized ticker symbols found in the query.\n"

    prompt = f"""
You are a professional financial analyst assistant AI.
You have access to real-time stock summaries and historical data.

User's Question:
\"\"\"{user_query}\"\"\"

{context}

Based on the above context and your expertise, provide a clear and informative answer.
"""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Gemini API Error: {e}"
