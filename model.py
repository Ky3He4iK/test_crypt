from time import time
from typing import Optional, Dict, Any, Union
from sys import stderr
import json

import numpy as np
from sklearn.linear_model import LinearRegression
import requests

import settings


def get_json(endpoint: str, params: Optional[Dict[str, Any]]) -> Optional[Union[dict, list]]:
    """
        Get json from binance future api
    """
    url = "https://fapi.binance.com/" + endpoint
    if params:
        url += "?" + "&".join(f"{a}={b}" for (a, b) in params.items())
    response = requests.get(url)
    if response.status_code != 200:
        stderr.write(f"{url} returns {response.status_code}: {response.text}")
    try:
        return json.loads(response.text)
    except json.decoder.JSONDecodeError as e:
        stderr.write(str(e))
    return None


class RealPriceModel:
    def __init__(self):
        btc_list = get_json("fapi/v1/klines", {"symbol": "BTCUSDT", "limit": 1500, "interval": "1m"})
        eth_list = get_json("fapi/v1/klines", {"symbol": "ETHUSDT", "limit": 1500, "interval": "1m"})
        btc_list_close = [float(e[4]) for e in btc_list]
        eth_list_close = [float(e[4]) for e in eth_list]

        x = np.array(btc_list_close).reshape((-1, 1))
        y = np.array(eth_list_close)
        self._model = LinearRegression(copy_X=True)
        self._model.fit(x, y)

        historic_data = (self._model.predict(x[-settings.tracking_period_minutes:]) -
                         y[-settings.tracking_period_minutes:]).flatten().tolist()
        self._history = [(d[6] / 1000, h) for (d, h) in zip(btc_list, historic_data)]
        self._last_saved_btc_price = btc_list_close[-1]
        self._last_saved_eth_price = None

    def update_btc_price(self, btc_price: float):
        self._last_saved_btc_price = btc_price

    def update_eth_price(self, eth_price: float) -> bool:
        # Проверять только изменившиеся значения
        if eth_price == self._last_saved_eth_price:
            return False
        self._last_saved_eth_price = eth_price

        # вычисление собственной цены
        eth_real_price = eth_price - (self._model.coef_[0] * self._last_saved_btc_price + self._model.intercept_)

        # проверка изменения собственной цены
        now, i, is_changed = time(), 0, False
        for i, (t, price) in enumerate(self._history):
            if now - t <= settings.tracking_period_minutes * 60:
                if abs(eth_real_price - price) > price * settings.tracking_threshold:
                    is_changed = True
                break

        # обновление истории
        self._history = self._history[i:]
        if now - self._history[-1][0] > 10:
            self._history.append((now, eth_real_price))
        return is_changed
