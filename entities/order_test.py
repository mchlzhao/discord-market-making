import unittest

from order import Order
from side import Side

class OrderTest(unittest.TestCase):
    def test_order(self):
        params = ('a', 1, 'buy', 1)
        order = Order.from_tuple(params)

        self.assertEqual(order.account_id, params[0])
        self.assertEqual(order.instrument_id, params[1])
        self.assertEqual(order.side, Side(params[2]))
        self.assertEqual(order.price, params[3])
