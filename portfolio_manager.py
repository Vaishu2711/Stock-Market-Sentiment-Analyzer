user_portfolios = {}

def add_stock(user_id, stock_symbol):
    if user_id not in user_portfolios:
        user_portfolios[user_id] = set()
    user_portfolios[user_id].add(stock_symbol.upper())
    return f"{stock_symbol.upper()} added to your portfolio."

def remove_stock(user_id, stock_symbol):
    if user_id in user_portfolios and stock_symbol.upper() in user_portfolios[user_id]:
        user_portfolios[user_id].remove(stock_symbol.upper())
        return f"{stock_symbol.upper()} removed from your portfolio."
    return f"{stock_symbol.upper()} not found in your portfolio."

def get_portfolio(user_id):
    return list(user_portfolios.get(user_id, []))

def check_alerts(user_id, sentiment_data):
    alerts = []
    portfolio = user_portfolios.get(user_id, [])
    for stock in portfolio:
        sentiment = sentiment_data.get(stock.upper(), "neutral")
        if sentiment.lower() == "negative":
            alerts.append(f"⚠️ Alert: Sentiment for {stock} is negative. Consider selling.")
    return alerts
