import requests
from twilio.rest import Client

class StockNewsNotifier:
    def __init__(self, stock_symbol, company_name, stock_api_key, news_api_key, twilio_sid, twilio_auth_token, twilio_number, recipient_number):
        self.stock_symbol = stock_symbol
        self.company_name = company_name
        self.stock_api_key = stock_api_key
        self.news_api_key = news_api_key
        self.twilio_client = Client(twilio_sid, twilio_auth_token)
        self.twilio_number = twilio_number
        self.recipient_number = recipient_number

    def fetch_stock_data(self):
        stock_endpoint = "https://www.alphavantage.co/query"
        params = {
            "function": "TIME_SERIES_DAILY",
            "symbol": self.stock_symbol,
            "apikey": self.stock_api_key,
        }
        response = requests.get(stock_endpoint, params=params)
        response.raise_for_status()
        return response.json()["Time Series (Daily)"]

    def calculate_price_difference(self, data):
        data_list = [value for value in data.values()]
        yesterday_close = float(data_list[0]["4. close"])
        day_before_yesterday_close = float(data_list[1]["4. close"])
        difference = yesterday_close - day_before_yesterday_close
        percent_diff = round((difference / yesterday_close) * 100)
        return difference, percent_diff

    def fetch_news(self):
        news_endpoint = "https://newsapi.org/v2/everything"
        params = {
            "qInTitle": self.company_name,
            "apiKey": self.news_api_key,
        }
        response = requests.get(news_endpoint, params=params)
        response.raise_for_status()
        return response.json()["articles"][:3]

    def format_articles(self, percent_diff, direction, articles):
        return [
            f"{self.stock_symbol}: {percent_diff}% {direction}\n"
            f"Headline: {article['title']}\nBrief: {article['description']}"
            for article in articles
        ]

    def send_notifications(self, messages):
        for message in messages:
            self.twilio_client.messages.create(
                body=message,
                from_=self.twilio_number,
                to=self.recipient_number
            )

    def run(self):
        try:
            stock_data = self.fetch_stock_data()
            difference, percent_diff = self.calculate_price_difference(stock_data)
            direction = "🔺" if difference > 0 else "🔻"

            if abs(percent_diff) > 1:
                news_articles = self.fetch_news()
                formatted_messages = self.format_articles(percent_diff, direction, news_articles)
                self.send_notifications(formatted_messages)
                print("Notifications sent successfully.")
            else:
                print("Price change is not significant enough to notify.")
        except Exception as e:
            print(f"An error occurred: {e}")


if __name__ == "__main__":
    notifier = StockNewsNotifier(
        stock_symbol="TSLA", # Company Symbol
        company_name="Tesla Inc", # Company Name
        stock_api_key="STOCK API KEY",
        news_api_key="NEWS API KEY",
        twilio_sid="TWILIO SID",
        twilio_auth_token="TWILIO TOKEN",
        twilio_number="+TWILIO NO",
        recipient_number="+YOUR PHONE NO"
    )
    notifier.run()

