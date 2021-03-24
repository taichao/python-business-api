import requests
import asyncio
from dct_business_api.base import ApiException, Base


def handle_response(res):
    data = res.json()
    if data.get('code') == ApiException.SUCCESS:
        return data['data']
    raise ApiException(data)


class RestClient(Base):
    def __init__(self, user_name, password, rest_base):
        super(RestClient, self).__init__(user_name, password, rest_base, None)

    def __token_url(self, url):
        return f'{url}&access_token={self.get_access_token()}'

    def get_order(self, order_id):
        url = self.__token_url(f'{self.rest_base}/thirdParty/getOrder?orderId={order_id}')
        return handle_response(requests.get(url))

    def get_order_trades(self, order_id):
        """
        :return: 获取订单成交信息。若无则返回[]
        """
        url = self.__token_url(f'{self.rest_base}/thirdParty/getOrderTrades?orderId={order_id}')
        return handle_response(requests.get(url))

    def get_account_balance(self, exchange, account_name):
        url = self.__token_url(
            f'{self.rest_base}/thirdParty/getAccountBalance?exchange={exchange}&accountName={account_name}')
        return handle_response(requests.get(url))

    def create_order(self, exchange, transaction_type, account_name,client_order_id, symbol, side, type, time_in_force, quantity, price,timeout=None):
        """

        :param client_order_id: 客户方订单id，针对同一个id，服务端只会处理一次
        """
        param = {
            'exchange': exchange,
            'transactionType': transaction_type,
            'accountName': account_name,
            'clientId': client_order_id,
            'symbol': symbol,
            'side': side,
            'type': type,
            'timeInForce': time_in_force,
            'quantity': quantity,
            'price': price
        }
        res = self.__create_order(**param)
        asyncio.ensure_future(self.cancel_order_later(res['orderId'],timeout)) 
        return res
    def cancel_order(self, order_id):
        url = self.rest_base + '/thirdParty/cancelOrderById'
        param = {
            'access_token': self.get_access_token(),
            'orderId': order_id
        }
        return handle_response(
            requests.post(url, data=param)
        )
    async def cancel_order_later(self,order_id,timeout=None):
        if timeout:
            await asyncio.sleep(timeout)
            self.cancel_order(order_id)

    def __create_order(self, **kwargs):
        url = self.rest_base + "/thirdParty/createOrder"
        access_token = self.get_access_token()
        param = {
            'access_token': access_token,
            **kwargs
        }
        res = requests.post(url, data=param)
        return handle_response(res)
