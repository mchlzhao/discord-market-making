import psycopg2

from decouple import config

from repos.postgres.account_repository import PostgresAccountRepository
from repos.postgres.instrument_repository import PostgresInstrumentRepository
from repos.postgres.position_repository import PostgresPositionRepository
from repos.postgres.trading_repository import PostgresTradingRepository
from repos.postgres.transaction_repository import PostgresTransactionRepository

from use_cases.trading.buy import BuyUseCase
from use_cases.trading.cancel import CancelUseCase
from use_cases.trading.sell import SellUseCase

class Controller:
    def __init__(self):
        self.conn = psycopg2.connect(
            host = 'localhost',
            port = 15432,
            dbname = 'market',
            user = 'postgres',
            options = '-c search_path="market_test"',
            password = config('POSTGRES_PW')
        )

        self.account_repository: PostgresAccountRepository = PostgresAccountRepository(self.conn)
        self.instrument_repository: PostgresInstrumentRepository = PostgresInstrumentRepository(self.conn)
        self.position_repository: PostgresPositionRepository = PostgresPositionRepository(self.conn)
        self.trading_repository: PostgresTradingRepository = PostgresTradingRepository(self.conn)
        self.transaction_repository: PostgresTransactionRepository = PostgresTransactionRepository(self.conn)

        self.buy_use_case: BuyUseCase = BuyUseCase(
            self.account_repository,
            self.instrument_repository,
            self.position_repository,
            self.trading_repository,
            self.transaction_repository
        )
        self.cancel_use_case: CancelUseCase = CancelUseCase(
            self.account_repository,
            self.instrument_repository,
            self.trading_repository
        )
        self.sell_use_case: SellUseCase = SellUseCase(
            self.account_repository,
            self.instrument_repository,
            self.position_repository,
            self.trading_repository,
            self.transaction_repository
        )
    
    def add_account(self, account_id, name, do_write):
        pass
    
    def buy(self, account_id, display_order, price):
        return self.buy_use_case.buy(account_id, display_order, price)
    
    def sell(self, account_id, display_order, price):
        return self.sell_use_case.sell(account_id, display_order, price)
    
    def cancel_buy(self, account_id, display_order):
        return self.cancel_use_case.cancel_buy(account_id, display_order)

    def cancel_sell(self, account_id, display_order):
        return self.cancel_use_case.cancel_sell(account_id, display_order)
    
    def mark_occurred(self, display_order, did_occur, do_write):
        pass
    
    def get_accounts_most_pos(self):
        '''
        returns the list of accounts, sorted in descending order of total positions
        used for paying out bonuses for taking risk
        ties are broken by random
        '''
        pass
    
    def pay_bonus(self):
        '''
        pays bonuses to players based on order from self.get_accounts_most_pos()
        returns list of pairs of accounts and their received payouts
        '''
        pass
    
    def clear_orders(self):
        '''
        clears all orders from all order books
        '''
        pass

    def clear_positions(self):
        '''
        clears all positions held by accounts
        '''
        pass

