import requests
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

BEARER_TOKEN = " Your Bearer Token"

def create_headers():
    return {"Authorization": f"Bearer {BEARER_TOKEN}"}

def search_tweets(query, max_results=20):
    url = "https://api.twitter.com/2/tweets/search/recent"
    params = {
        "query": query,
        "tweet.fields": "text,lang",
        "max_results": max_results
    }
    headers = create_headers()
    response = requests.get(url, headers=headers, params=params)
    if response.status_code != 200:
        return []
    tweets = response.json().get("data", [])
    return [tweet["text"] for tweet in tweets if tweet["lang"] == "en"]

def get_tweet_sentiment(stock_symbol):
    tweets = search_tweets(f"${stock_symbol} stock")
    analyzer = SentimentIntensityAnalyzer()
    scores = [analyzer.polarity_scores(tweet) for tweet in tweets]
    if not scores:
        return None, []
    avg = {
        "neg": sum(s["neg"] for s in scores) / len(scores),
        "neu": sum(s["neu"] for s in scores) / len(scores),
        "pos": sum(s["pos"] for s in scores) / len(scores),
        "compound": sum(s["compound"] for s in scores) / len(scores),
    }
    return avg, tweets
