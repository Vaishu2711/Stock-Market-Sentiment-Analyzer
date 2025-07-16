import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import io

analyzer = SentimentIntensityAnalyzer()

def fetch_google_news(stock):
    feed = feedparser.parse(f"https://news.google.com/rss/search?q={stock}+stock")
    return [entry.title + " " + entry.description for entry in feed.entries[:10]]

def get_sentiment(texts):
    scores = [analyzer.polarity_scores(text) for text in texts]
    avg = {
        "neg": sum(s["neg"] for s in scores) / len(scores),
        "neu": sum(s["neu"] for s in scores) / len(scores),
        "pos": sum(s["pos"] for s in scores) / len(scores),
        "compound": sum(s["compound"] for s in scores) / len(scores),
    }
    return avg, scores

def generate_wordcloud(texts):
    wc = WordCloud(width=800, height=400, background_color="white").generate(" ".join(texts))
    buffer = io.BytesIO()
    wc.to_image().save(buffer, format='PNG')
    buffer.seek(0)
    return buffer
