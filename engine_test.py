from entities.instrument import Instrument
from entities.order import Order
from entities.side import Side

from repos.account_repository import AccountRepository
from repos.instrument_repository import InstrumentRepository
from repos.position_repository import PositionRepository
from repos.trading_repository import TradingRepository

class Engine:
    def __init__(self, account_repository: AccountRepository, instrument_repository: InstrumentRepository,
            position_repository: PositionRepository, trading_repository: TradingRepository):

        self.account_repository: AccountRepository = account_repository
        self.instrument_repository: InstrumentRepository = instrument_repository
        self.position_repository: PositionRepository = position_repository
        self.trading_repository: TradingRepository = trading_repository

    def is_buy_in_cross(self, account_id, display_order, price):
        existing_sell = self.trading_repository.get_existing_order(account_id, display_order, 'sell')
        return existing_sell is not None and existing_sell[4] <= price

    def is_sell_in_cross(self, account_id, display_order, price):
        existing_buy = self.trading_repository.get_existing_order(account_id, display_order, 'buy')
        return existing_buy is not None and price <= existing_buy[4]
    
    def process_bid(self, account_id, display_order, side, price):
        if side == Side.BUY:
            return self.process_buy(account_id, display_order, price)
        
        return self.process_sell(account_id, display_order, price)

    # assumes buys do not cross with existing sells
    def process_buy(self, account_id, display_order, price):
        existing = self.trading_repository.get_existing_order(account_id, display_order, 'buy')
        if existing is not None:
            self.process_cancel(account_id, display_order, 'buy')

        account = self.account_repository.get_account_using_id(account_id)
        instrument = self.instrument_repository.get_instrument_using_display_order(display_order)
        order = Order(account, instrument, Side.BUY, price)

        try:
            best_sell = self.trading_repository.get_best_sell(instrument, 1)[0]
        except IndexError:
            best_sell = None
        print('best sell =', best_sell)

        if best_sell is None or price < best_sell[4]:
            self.trading_repository.add_order(order, 'unfilled')
            return None
        
        self.trading_repository.add_order(order, 'filled')
        self.trading_repository.update_order_status_using_order_id(best_sell[0], 'filled')

        print('%s bought from %s instrument display order = %d price = %d' %
            (account_id, best_sell[2], best_sell[5], best_sell[4]))
        
        return {
            'buyer_id': account_id,
            'seller_id': best_sell[2],
            'is_buyer_maker': False,
            'instrument_id': best_sell[5],
            'display_order': display_order,
            'price': best_sell[4]
        }

    def process_sell(self, account_id, display_order, price):
        existing = self.trading_repository.get_existing_order(account_id, display_order, 'sell')
        if existing is not None:
            self.process_cancel(account_id, display_order, 'sell')

        account = self.account_repository.get_account_using_id(account_id)
        instrument = self.instrument_repository.get_instrument_using_display_order(display_order)
        order = Order(account, instrument, Side.SELL, price)
        
        try:
            best_buy = self.trading_repository.get_best_buy(instrument, num_results = 1)[0]
        except IndexError:
            best_buy = None
        print('best buy =', best_buy)

        if best_buy is None or best_buy[4] < price:
            self.trading_repository.add_order(order, 'unfilled')
            return None
        
        self.trading_repository.add_order(order, 'filled')
        self.trading_repository.update_order_status_using_order_id(best_buy[0], 'filled')

        print('%s sold to %s instrument display order = %d price = %d' % 
            (account_id, best_buy[2], best_buy[5], best_buy[4]))

        return {
            'buyer_id': best_buy[2],
            'seller_id': account_id,
            'is_buyer_maker': True,
            'instrument_id': best_buy[5],
            'display_order': display_order,
            'price': best_buy[4]
        }

    def process_cancel(self, account_id, display_order, side):
        account = self.account_repository.get_account_using_id(account_id)
        instrument = self.instrument_repository.get_instrument_using_display_order(display_order)
        order = Order(account, instrument, side, -1)

        self.trading_repository.update_order_status(order, 'cancelled')
