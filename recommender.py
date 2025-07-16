def make_recommendation(score):
    if score >= 0.4:
        return "🔼 Strong Buy"
    elif score >= 0.1:
        return "⬆️ Buy"
    elif score <= -0.4:
        return "🔻 Strong Sell"
    elif score <= -0.1:
        return "⬇️ Sell"
    else:
        return "⏸️ Hold"
