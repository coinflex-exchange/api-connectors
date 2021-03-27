"""
This is a simple WebSocket adapter to connect to CoinFLEX's API.
You can use methods whose names begin with “subscribe”, and get resultant data by calling the 'get' methods.
All of the available WebSocket endpoints are featured in this adapter.
Methods denoted as "Private" require authentication, but public methods do not.
Please check the official API documentation here https://docs.coinflex.com/#change-log if you have any questions.
Please contact us via e-mail at contact@coinflex.com or telegram https://t.me/coinflex_EN if you require assistance.
"""
import threading
from time import sleep
import json
import logging
import hashlib
import base64
import time
import hmac
from typing import Union, List

import websocket


class CoinFLEXWebSocket:
    """WebSocket Adapter"""
    MAX_DATA_CAPACITY = 200
    INTERVALS = ('60s', '300s', '900s', '1800s', '3600s', '7200s', '14400s', '86400s')

    def __init__(self, url, market, api_key=None, api_secret=None):
        if api_key is not None and api_secret is None:
            raise ValueError('api_secret is required if api_key is provided')
        if api_key is None and api_secret is not None:
            raise ValueError('api_key is required if api_secret is provided')

        self._url = url
        self._api_key = api_key
        self._api_secret = api_secret
        self._market = market

        '''Initialize'''
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.DEBUG, format='%(asctime)s: %(message)s',
)
        self.logger.debug('Initializing WebSocket.')

        self.data = {}
        self.exited = False
        self.auth = False

        # We can subscribe right in the connection querystring, so let's build that.
        # Subscribe to all pertinent endpoints.

        self.logger.debug('Connecting to %s', url)
        self.__connect(url)

    def exit(self):
        """Call this to exit - will close WebSocket."""
        self.exited = True
        self.ws.close()

    def __connect(self, url):
        """Connect to the WebSocket in a thread."""
        self.logger.info('Starting thread')

        self.ws = websocket.WebSocketApp(url,
                                         on_message=self.__on_message,
                                         on_close=self.__on_close,
                                         on_open=self.__on_open,
                                         on_error=self.__on_error,
                                         keep_running=True)

        self.wst = threading.Thread(target=lambda: self.ws.run_forever(ping_interval=30, ping_timeout=15))
        self.wst.daemon = True
        self.wst.start()
        self.logger.info('Started thread')

        # Wait for connect before continuing
        retry_times = 5
        while not self.ws.sock or not self.ws.sock.connected and retry_times:
            sleep(1)
            retry_times -= 1
        if retry_times == 0 and not self.ws.sock.connected:
            self.logger.error('Could not connect to WebSocket! Exiting.')
            self.exit()
            raise websocket.WebSocketTimeoutException('Error！Could not connect to WebSocket!')

        if self._api_key and self._api_secret:
            self.__authenticate()

    def __on_message(self, message):
        """Handler for parsing WS messages."""
        message = json.loads(message)
        self.logger.debug('%s', message)

        if 'table' in message:
            self.data[message['table']].append(message)
            if len(self.data[message['table']]) > self.MAX_DATA_CAPACITY:
                self.data[message['table']] = self.data[message['table']][self.MAX_DATA_CAPACITY // 2:]

        if 'event' in message:
            if message['event'] in ('placeorder', 'cancelorder', 'modifyorder'):
                if 'order' in self.data:
                    self.data['order'].append(message)
                else:
                    self.logger.debug('Call "subscribe_order()" to receive order ACKs and updates using get_order')
            elif message['event'] == 'Welcome':
                self.auth = True
                self.logger.debug('Authentication success %s.', message)
            elif message['event'] == 'subscribe' and message['success']:
                self.logger.debug('Successfully subscribed to %s', message)

    def __on_error(self, error):
        """Called on fatal WebSocket errors. We exit on these."""
        if not self.exited:
            self.logger.error('Error: %s', error)
            raise websocket.WebSocketException(error)

    def __on_open(self):
        """Called when the WS opens."""
        self.logger.debug('WebSocket Opened.')

    def __on_close(self):
        """Called on WebSocket close."""
        self.logger.debug('WebSocket Closed')

    def __authenticate(self):
        """Authentication is required for private channels and order submission."""
        timestamp = str(int(time.time() * 1000))
        secret = bytes(self._api_secret, 'utf-8')
        message = bytes(timestamp + 'GET' + '/auth/self/verify', 'utf-8')
        signature = base64.b64encode(
            hmac.new(secret, message, digestmod=hashlib.sha256).digest()
        ).decode('utf-8')
        data = {'apiKey': self._api_key, 'timestamp': timestamp, 'signature': signature}
        auth = json.dumps({'op': 'login', 'data': data, 'tag': 'hello'})
        self.ws.send(auth)

    # ------------------------ #
    # Private Order Management #
    # ------------------------ #

    def place_limit_order(self, cl_o_id: int, side: str, price: float, quantity: float,
                          tif: str, tag: Union[int, str] = 1):
        """Place a limit order."""
        place_limit = json.dumps(
            {
                'op': 'placeorder',
                'data': {
                    'clientOrderId': cl_o_id,
                    'marketCode': self._market,
                    'side': side,
                    'orderType': 'LIMIT',
                    'quantity': quantity,
                    'timeInForce': tif,
                    'price': price,
                },
                'tag': tag
            }
        )
        self.ws.send(place_limit)

    def place_market_order(self, cl_o_id: int, side: str, quantity: float, tag: Union[int, str] = 1):
        """Place a market order."""
        place_market = json.dumps(
            {
                'op': 'placeorder',
                'data': {
                    'clientOrderId': cl_o_id,
                    'marketCode': self._market,
                    'side': side,
                    'orderType': 'MARKET',
                    'quantity': quantity,
                },
                'tag': tag,
            }
        )
        self.ws.send(place_market)

    def place_stop_order(self, cl_o_id: int, side: str,
                         stop_price: float, limit_price: float,
                         quantity: float, tif: str,
                         tag: Union[int, str] = 1):
        """Place a stop order."""
        place_stop = json.dumps(
            {
                'op': 'placeorder',
                'data': {
                    'clientOrderId': cl_o_id,
                    'marketCode': self._market,
                    'side': side,
                    'orderType': 'STOP',
                    'quantity': quantity,
                    'timeInForce': tif,
                    'stopPrice': stop_price,
                    'limitPrice': limit_price
                },
                'tag': tag
            }
        )
        self.ws.send(place_stop)

    def batch_place_order(self, orders: List[dict], tag: Union[int, str] = 1):
        """
        Place batch orders using an order dataArray
        dataArrays can hold up to 20 orders,
        an example of one featuring a limit and market order is shown below.
        dataArrays support limit, market, and stop orders.
        See place_stop_order() for proper stop order syntax.
        [
            {
              "clientOrderId": 1,
              "marketCode": "ETH-USD-SWAP-LIN",
              "side": "BUY",
              "orderType": "LIMIT",
              "quantity": 10,
              "timeInForce": "MAKER_ONLY",
              "price": 1495
            },
            {
              "clientOrderId": 2,
              "marketCode": "ETH-USD-SWAP-LIN",
              "side": "BUY",
              "orderType": "MARKET",
              "quantity": 10
            },
        ]
        """
        if len(orders) > 20:
            self.logger.debug('Batch requests are limited to 20 orders!')
        else:
            self.ws.send(
                json.dumps(
                    {'op': 'placeorders', 'dataArray': orders, 'tag': tag}
                )
            )

    def modify_order(self, o_id: int, side: str, price: float, quantity: float, tag: Union[int, str] = 1):
        """Modify an order with orderId and marketCode."""
        modify = json.dumps(
            {
                'op': 'modifyorder',
                'data': {
                    'marketCode': self._market,
                    'orderId': o_id,
                    'side': side,
                    'price': price,
                    'quantity': quantity,
                },
                'tag': tag
            }
        )
        self.ws.send(modify)

    def batch_modify_order(self, orders: List[dict], tag: Union[int, str] = 1):
        """
        Modify orders in a batch using an order dataArray
        dataArrays can hold up to 20 orders, an example of
        one featuring two limit orders is shown below.
        dataArrays support limit, market, and stop orders.
        See place_stop_order() for proper stop order syntax.
        [
            {
              "orderId": 304390972051898366,
              "marketCode": "ETH-USD-SWAP-LIN",
              "side": "BUY",
              "orderType": "LIMIT",
              "quantity": 10,
              "price": 1495
            },
            {
              "orderId": 304390972051898367,
              "marketCode": "ETH-USD-SWAP-LIN",
              "side": "SELL",
              "orderType": "LIMIT",
              "quantity": 10,
              "price": 1500
            },
        ]
        """
        if len(orders) > 20:
            self.logger.debug('Batch requests are limited to 20 orders!')
        else:
            self.ws.send(
                json.dumps(
                    {'op': 'modifyorders', 'dataArray': orders, 'tag': tag}
                )
            )

    def cancel_order(self, o_id: str, tag: Union[int, str] = 1):
        """Cancel an order with orderId and MarketCode."""
        cancel = json.dumps(
            {
                'op': 'cancelorder',
                'data': {
                    'marketCode': self._market,
                    'orderId': o_id,
                },
                'tag': tag
            }
        )
        self.ws.send(cancel)

    def batch_cancel_order(self, orders: List[dict], tag: Union[int, str] = 1):
        """
        Cancel orders in a batch using an order dataArray
        dataArrays can hold up to 20 orders, an example of
        one featuring two limit orders is shown below.
        cancel dataArrays support limit and stop orders.
        See place_stop_order() for proper stop order syntax.
        [
            {
              "orderId": 1,
              "marketCode": "ETH-USD-SWAP-LIN",
            },
            {
              "orderId": 2,
              "marketCode": "ETH-USD-SWAP-LIN",
            },
        ]
        """
        if len(orders) > 20:
            self.logger.debug('Batch requests are limited to 20 orders!')
        else:
            self.ws.send(
                json.dumps(
                    {'op': 'cancelorders', 'dataArray': orders, 'tag': tag}
                )
            )

    # ---------------- #
    # Private Channels #
    # ---------------- #

    def subscribe_balance(self, coin: str = 'all'):
        """Subscribe to balances - all balances by default."""
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['balance:' + coin], 'tag': 1}))
        if 'balance' not in self.data:
            self.data['balance'] = []

    def subscribe_position(self):
        """Subscribe to positions in the selected market."""
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['position:' + self._market], 'tag': 1}))
        if 'position' not in self.data:
            self.data['position'] = []

    def subscribe_order(self):
        """Subscribe to orders in the selected market."""
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['order:' + self._market], 'tag': 1}))
        if 'order' not in self.data:
            self.data['order'] = []

    def get_balance(self):
        return self._get_data('balance')

    def get_position(self):
        return self._get_data('position')

    def get_order(self):
        return self._get_data('order')

    # --------------- #
    # Public Channels #
    # --------------- #

    def subscribe_liquidation(self):
        """Subscribe to Requests for Quotes from all markets."""
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['liquidationRFQ'], 'tag': 1}))
        if 'RFQ' not in self.data:
            self.data['liquidationRFQ'] = []

    def subscribe_depth(self, level: Union[int, str] = None):
        """Subscribe to the L5, L10, L25, or full order book snapshots - default full order book snapshots."""
        depth = 'depth'
        if level:
            if int(level) in (5, 10, 25):
                depth = 'depthL' + str(level)
            else:
                self.logger.debug('level %s is not valid.', level)
                return
        self.ws.send(json.dumps({'op': 'subscribe', 'args': [depth + ':' + self._market], 'tag': 1}))
        if 'depth' not in self.data:
            self.data[depth] = []

    def subscribe_trade(self):
        """Subscribe to trades in the selected market."""
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['trade:' + self._market], 'tag': 1}))
        if 'trade' not in self.data:
            self.data['trade'] = []

    def subscribe_ticker(self):
        """Subscribe to selected market ticker updates."""
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['ticker:' + self._market], 'tag': 1}))
        if 'ticker' not in self.data:
            self.data['ticker'] = []

    def subscribe_kline(self, interval: str):
        """Subscribe to selected market Kline updates."""
        params = interval + ':' + self._market
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['candles' + params], 'tag': 1}))
        if interval not in self.data:
            self.data['candles' + interval] = []

    def subscribe_market(self):
        self.ws.send(json.dumps({'op': 'subscribe', 'args': ['market:' + self._market], 'tag': 1}))
        if 'market' not in self.data:
            self.data['market'] = []

    def _get_data(self, channel):
        if channel not in self.data:
            self.logger.debug('Not subscribed to the %s channel.', channel)
            return []
        if len(self.data[channel]) == 0:
            return []
        return self.data[channel].pop(0)

    def get_liquidation(self):
        return self._get_data('liquidationRFQ')

    def get_depth(self, level: Union[int, str] = None):
        depth = 'depth'
        if level:
            if int(level) in (5, 10, 25):
                depth = 'depthL' + str(level)
            else:
                self.logger.debug('level %s is invalid.', level)
        return self._get_data(depth)

    def get_trade(self):
        return self._get_data('trade')

    def get_ticker(self):
        return self._get_data('ticker')

    def get_kline(self, interval: str):
        if interval in self.INTERVALS:
            return self._get_data('candles' + interval)
        self.logger.debug('interval %s is invalid.', interval)

    def get_market(self):
        return self._get_data('market')
