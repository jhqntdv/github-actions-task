import requests
import logging
import os
import pandas as pd
from datetime import timedelta

# Set up logging
logger1 = logging.getLogger('logger1')
logger1.setLevel(logging.INFO)
handler1 = logging.FileHandler('status.log')
handler1.setLevel(logging.INFO)
formatter1 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler1.setFormatter(formatter1)
logger1.addHandler(handler1)

logger2 = logging.getLogger('logger2')
logger2.setLevel(logging.INFO)
handler2 = logging.FileHandler('status_signal.log')
handler2.setLevel(logging.INFO)
formatter2 = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler2.setFormatter(formatter2)
logger2.addHandler(handler2)

# Finnhub Client
class Client:
    API_URL = "https://api.finnhub.io/api/v1"
    DEFAULT_TIMEOUT = 10

    def __init__(self, api_key, proxies=None):
        self._session = self._init_session(api_key, proxies)

    @staticmethod
    def _init_session(api_key, proxies):
        session = requests.session()
        session.headers.update({"Accept": "application/json",
                                "User-Agent": "finnhub/python"})
        session.params = {"token": api_key}
        if proxies is not None:
            session.proxies.update(proxies)
        return session

    def _request(self, method, endpoint, params=None):
        url = f"{self.API_URL}/{endpoint}"
        response = self._session.request(method, url, params=params, timeout=self.DEFAULT_TIMEOUT)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def get_upcoming_ipo(self, start_date, end_date):
        params = {
            'from': start_date,
            'to': end_date
        }
        return self._request('GET', 'calendar/ipo', params=params)

# Signal function for IPO data
def signal_ipo(data):
    count_withdrawn, count_priced, count_expected, count_filed = 0, 0, 0, 0
    total_shares_value = 0
    largest_ipo = {"name": "", "status": "", "totalSharesValue": 0}
    latest_withdrawn = {"name": "", "date": ""}
    latest_priced = {"name": "", "date": "", "totalSharesValue": 0}

    for item in data['ipoCalendar']:
        name = item.get('name', '')
        totalSharesValue = item.get('totalSharesValue', 0)
        status = item.get('status', '')
        date = item.get('date', '')

        if totalSharesValue:
            total_shares_value += totalSharesValue
            if totalSharesValue > largest_ipo["totalSharesValue"]:
                largest_ipo = {"name": name, "status": status, "totalSharesValue": totalSharesValue}

        if status == 'priced':
            count_priced += 1
            if not latest_priced["date"] or date > latest_priced["date"]:
                latest_priced = {"name": name, "date": date, "totalSharesValue": totalSharesValue}
        elif status == 'filed':
            count_filed += 1
        elif status == 'expected':
            count_expected += 1
        elif status == 'withdrawn':
            count_withdrawn += 1
            if not latest_withdrawn["date"] or date > latest_withdrawn["date"]:
                latest_withdrawn = {"name": name, "date": date}

    a = (count_priced + count_expected)
    b = (count_priced + count_expected + count_filed)
    c = count_priced
    d = (count_priced + count_expected)

    logger2.info(f"For the last 14 days, {a} / {b} companies filed IPO with price, {c} / {d} IPOs are expected, Total IPOs value: {total_shares_value/1e6:.3f}M")
    logger2.info(f"Largest IPO: {largest_ipo['name']} with totalSharesValue: {largest_ipo['totalSharesValue']/1e6:.3f}M")
    logger2.info(f"Latest IPO is {latest_priced['name']} on {latest_priced['date']} with totalSharesValue: {latest_priced['totalSharesValue']/1e6:.3f}M")
    logger2.info(f"Latest IPO withdrawn: {latest_withdrawn['name']} on {latest_withdrawn['date']}")

    result = (c, d)
    return result

if __name__ == "__main__":
    try:
        FINNHUB_API_KEY = os.environ["FINNHUB_API_KEY"]
    except KeyError:
        FINNHUB_API_KEY = ""
        logger1.error("FINNHUB_API_KEY not found in env.")

    today = pd.Timestamp.today().tz_localize('UTC').strftime('%Y-%m-%d')

    if FINNHUB_API_KEY:
        client = Client(FINNHUB_API_KEY)
        start_date = (pd.Timestamp.today().tz_localize('UTC') - timedelta(days=14)).strftime('%Y-%m-%d')
        data = client.get_upcoming_ipo(start_date, today)
        if data:
            signal_ipo(data)