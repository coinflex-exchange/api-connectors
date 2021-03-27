import time
import coinflex_ws

key = ''        # Add your api key here
secret = ''     # Add your api secret here
url = 'wss://v2stgapi.coinflex.com/v2/websocket'    # Change to 'wss://v2api.coinflex.com/v2/websocket to access live trading
market = ''     # Select your market here

ws = coinflex_ws.CoinFLEXWebSocket(
    url=url,
    market='',
    api_key=key,
    api_secret=secret
)

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

# ws.place_limit_order(1, 'BUY', 10,  0.001, 'GTC', 1)
# ws.place_stop_order(1, 'BUY', 50000, 60000, 0.001, 'GTC', 2)
# ws.place_market_order(1, 'BUY', 0.001, time.time())
# ws.cancel_order('304397024272106384', 3)
# ws.modify_order('304397024272106383', 'BUY', 4000, 0.1, 'modify1')


'''
ws.batch_place_order([
            {
              "clientOrderId": 1,
              "marketCode": "BTC-USD-SWAP-LIN",
              "side": "BUY",
              "orderType": "LIMIT",
              "quantity": 0.001,
              "timeInForce": "MAKER_ONLY",
              "price": 1495
            },
            {
              "clientOrderId": 2,
              "marketCode": "BTC-USD-SWAP-LIN",
              "side": "BUY",
              "orderType": "MARKET",
              "quantity": 0.001
            },
        ])

'''
'''
ws.batch_modify_order([
            {
              "orderId": 304390972051898363,
              "marketCode": "BTC-USD-SWAP-LIN",
              "side": "SELL",
              "orderType": "LIMIT",
              "quantity": 0.001,
              "price": 60005
            },
        ])
'''

'''
ws.batch_cancel_order([
            {
              "orderId": "304390972051898366",
              "marketCode": "BTC-USD-SWAP-LIN",
            },
        ])
'''

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
