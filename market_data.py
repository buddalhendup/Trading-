import requests


def get_btc_price():
    """Gets live BTC price from Coinbase public API.

    This is only used for paper practice. No real orders are placed.
    """
    try:
        url = 'https://api.coinbase.com/v2/prices/BTC-USD/spot'
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data['data']['amount'])
    except Exception:
        return 0.0
