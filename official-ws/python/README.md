# WebSocket Adapter
This is a simple CoinFLEX WebSocket adapter.

# Installation
pip install coinflex-ws

# Usage
All CoinFLEX WebSocket streams and requests are available in this package.

Import the CoinFLEX WebSocket library and initialise an instance of the client:
```python
import coinflex_ws

ws = coinflex_ws.CoinFLEXWebSocket(
    url="wss://v2stgapi.coinflex.com/v2/websocket",	# Testnet endpoint; live endpoint is "wss://v2api.coinflex.com/v2/websocket"
    api_key='',
    api_secret=''
)
```

API keys, api\_key and api_secret, are required to access private streams and requests.

## Streaming data and making requests
This wrapper supports all of the WebSocket channels on the docs (docs.coinflex.com).

When a get method, such as get_depth(), returns an empty string it indicates that no relevant data has been received by the client yet.

```python
# Subscribe to WebSocket streams

# Public endpoints
# ws.subscribe_liquidation()
ws.subscribe_depth(25)
# ws.subscribe_trade()
# ws.subscribe_ticker()
# ws.subscribe_kline('60s')
# ws.subscribe_market()

# Private endpoints
# ws.subscribe_balance()
# ws.subscribe_position()
# ws.subscribe_order()

# Order Management
# ws.place_limit_order(1, 'BUY', 10,  0.001, 'GTC', 1)		# clientOrderId, side, price, quantity, time in force, tag
# ws.place_stop_order(1, 'BUY', 50000, 60000, 0.001, 'GTC', 2)  # clientOrderId, side, stopPrice, limitPrice, quantity, time in force, tag
# ws.place_market_order(1, 'BUY', 0.001, time.time())		# clientOrderId, side, quantity, tag
# ws.cancel_order('304397024272106384', 3)				# orderId, tag
# ws.modify_order('304397024272106383', 'BUY', 4000, 0.1, 'modify1')	# orderId, side, price, quantity, tag

# Get responses forever
while True:
    # print(ws.get_liquidation())
    print(ws.get_depth(25))
    # print(ws.get_trade())
    # print(ws.get_ticker())
    # print(ws.get_kline('60s'))
    # print(ws.get_market())

    # print(ws.get_balance())
    # print(ws.get_position())
    # print(ws.get_order())

    time.sleep(0.5)
```
See a full usage example in test.py at https://github.com/coinflex-exchange/api-connectors/tree/main/official-ws/python.
