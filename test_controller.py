import unittest

from account import Account
from controller import Controller
from util import Side

import settings

do_write = True

class TestController(unittest.TestCase):
    def setUp(self):
        self.controller = Controller('Local Testing', 'app_local.log', settings.PRODUCTS, True)
        for id, name in zip(range(0, 4), 'abcd'):
            self.controller.add_account(id, name, do_write)
        self.accounts = self.controller.accounts

    def tearDown(self):
        del self.controller

    def test_all(self):
        order_book0 = self.controller.engine.order_books[settings.PRODUCTS[0]]

        # posting buy and sell
        result = self.controller.process_bid(0, 1, Side.BUY, 50, do_write)
        self.assertEqual(result[0], 0)
        self.assertIs(order_book0.buy_orders[50][0], self.accounts[0])

        result = self.controller.process_bid(0, 1, Side.SELL, 60, do_write)
        self.assertEqual(result[0], 0)
        self.assertIs(order_book0.sell_orders[60][0], self.accounts[0])

        # price clamping and in cross check
        result = self.controller.process_bid(0, 1, Side.SELL, 40, do_write)
        self.assertEqual(result[0], -2)
        self.assertEqual(len(order_book0.sell_orders[40]), 0)
        self.assertIs(order_book0.sell_orders[60][0], self.accounts[0])

        # price not in bounds
        result = self.controller.process_bid(0, 1, Side.BUY, -1, do_write)
        self.assertEqual(result[0], -3)
        result = self.controller.process_bid(0, 1, Side.SELL, 101, do_write)
        self.assertEqual(result[0], -3)

        # product does not exist
        result = self.controller.process_bid(2, 0, Side.BUY, 50, do_write)
        self.assertEqual(result[0], -4)

        # cancelling 
        result = self.controller.process_cancel(0, 1, Side.SELL, do_write)
        self.assertEqual(result, 0)
        self.assertEqual(len(order_book0.sell_orders[60]), 0)

        # non existent cancel
        result = self.controller.process_cancel(1, 1, Side.BUY, do_write)
        self.assertEqual(result, -1)

        # rebidding
        result = self.controller.process_bid(0, 1, Side.SELL, 100, do_write)
        self.assertEqual(result[0], 0)
        self.assertEqual(len(order_book0.sell_orders[60]), 0)
        self.assertIs(order_book0.sell_orders[100][0], self.accounts[0])

        # trade
        result = self.controller.process_bid(1, 1, Side.BUY, 100, do_write)
        self.assertEqual(result[0], 0)
        self.assertIsNotNone(result[1])
        self.assertEqual(self.accounts[0].balance, 100)
        self.assertEqual(self.accounts[0].inventory[settings.PRODUCTS[0]], -1)
        self.assertEqual(self.accounts[1].balance, -100)
        self.assertEqual(self.accounts[1].inventory[settings.PRODUCTS[0]], 1)

        # reaching position limit
        for _ in range(1, settings.POSITION_LIMIT):
            self.controller.process_bid(0, 1, Side.SELL, 100, do_write)
            self.controller.process_bid(1, 1, Side.BUY, 100, do_write)
        
        self.assertEqual(self.accounts[0].inventory[settings.PRODUCTS[0]], -settings.POSITION_LIMIT)
        self.assertEqual(self.accounts[1].inventory[settings.PRODUCTS[0]], settings.POSITION_LIMIT)

        result = self.controller.process_bid(0, 1, Side.SELL, 100, do_write)
        self.assertEqual(result[0], -1)
        self.assertEqual(len(order_book0.sell_orders[100]), 0)
        result = self.controller.process_bid(1, 1, Side.BUY, 100, do_write)
        self.assertEqual(result[0], -1)
        self.assertEqual(len(order_book0.buy_orders[100]), 0)

        # marking occurred
        self.assertEqual(self.accounts[0].balance, 500)
        self.assertEqual(self.accounts[1].balance, -500)
        self.controller.mark_occurred(1, True, do_write)
        self.assertEqual(self.accounts[0].balance, 0)
        self.assertEqual(self.accounts[1].balance, 0)

        self.controller.process_bid(0, 2, Side.SELL, 50, do_write)
        self.controller.process_bid(1, 2, Side.BUY, 50, do_write)
        self.assertEqual(self.accounts[0].balance, 50)
        self.assertEqual(self.accounts[1].balance, -50)
        self.controller.mark_occurred(2, False, do_write)
        self.assertEqual(self.accounts[0].balance, 50)
        self.assertEqual(self.accounts[1].balance, -50)

        # getting bonus order
        ordered_accounts = self.controller.get_accounts_most_pos()
        self.assertEqual(self.accounts[0].total_positions, 6)
        self.assertIn(self.accounts[0], ordered_accounts[:2])

        # clearing orders
        self.controller.clear_orders()
        self.assertEqual(len(order_book0.buy_orders[50]), 0)

        # clearing positions
        self.controller.clear_positions()
        self.assertEqual(self.accounts[0].total_positions, 0)