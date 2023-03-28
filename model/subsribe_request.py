from dataclasses import dataclass
import json
from typing import List, Dict, Union


@dataclass
class SubscribeRequest:
    type: str
    # product_ids: List[str]
    product_ids: list
    # channels: List[Union[str, Dict[str, Union[str, List[str]]]]]
    channels: list


def default_request() -> SubscribeRequest:
    return SubscribeRequest(
        type="subscribe",
        product_ids=[
            "ETH-USD",
            "ETH-EUR"
        ],
        channels=[
            "level2",
            "heartbeat",
            {
                "name": "ticker",
                "product_ids": [
                    "ETH-BTC",
                    "ETH-USD"
                ]
            },
            {
                "name": "status"
            }
        ]
    )


if __name__ == '__main__':
    print(json.dumps({
    "type": "subscribe",
    "product_ids": [
        "ETH-USD",
        "ETH-EUR"
    ],
    "channels": [
        "level2",
        "heartbeat",
        {
            "name": "ticker",
            "product_ids": [
                "ETH-BTC",
                "ETH-USD"
            ]
        },{
                "name": "status"
            }
    ]
}))
