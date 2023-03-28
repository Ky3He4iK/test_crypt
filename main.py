import asyncio
import signal
import json
from asyncio.exceptions import CancelledError
import websockets
from websockets.exceptions import ConnectionClosed
from model import RealPriceModel
import settings
from time import sleep


is_running = True


async def client():
    def close():
        global is_running
        is_running = False
        loop.create_task(websocket.close())

    model = RealPriceModel()
    uri = settings.base_uri + f"?streams={settings.primary_pair.lower()}@{settings.stream}/" \
                              f"{settings.secondary_pair.lower()}@{settings.stream}"
    # uri = "wss://fstream.binance.com/ws/bnbusdt@aggTrade"
    loop = asyncio.get_running_loop()
    global is_running
    print("Started")

    while is_running:
        async with websockets.connect(uri) as websocket:
            # Close the connection when receiving SIGTERM/SIGINT
            loop.add_signal_handler(signal.SIGTERM, close)
            loop.add_signal_handler(signal.SIGINT, close)

            # latency = await (await websocket.ping())
            # print(f"Задержка: {round(latency, 4)}s")

            while True:
                try:
                    message = await websocket.recv()
                    # print(message)
                    m = json.loads(message)
                    symbol, bid, ask = m["data"]["s"], float(m["data"]["b"]), float(m["data"]["a"])
                    cost = (bid + ask) / 2
                    if symbol == settings.primary_pair:
                        model.update_btc_price(cost)
                    elif symbol == settings.secondary_pair:
                        if model.update_eth_price(cost):
                            print("Значительное изменение стоимости:", cost)
                except ConnectionClosed:
                    sleep(0.1)  # binance disconnect every 24h. Sleep to avoid spamming in case of error
                    break
                except CancelledError:
                    is_running = False
                    break


if __name__ == '__main__':
    asyncio.run(client())
