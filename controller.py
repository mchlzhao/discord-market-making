import psycopg2

from decouple import config
from typing import Tuple

from repos.postgres.account_repository import PostgresAccountRepository
from repos.postgres.instrument_repository import PostgresInstrumentRepository
from repos.postgres.position_repository import PostgresPositionRepository
from repos.postgres.trading_repository import PostgresTradingRepository
from repos.postgres.transaction_repository import PostgresTransactionRepository

from use_cases.admin.add_account import AddAccountUseCase
from use_cases.admin.mark_instrument import MarkInstrumentUseCase
from use_cases.admin.pay_bonus import PayBonusUseCase
from use_cases.api.rest_api import ApiUseCase
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
            options = '-c search_path="market"',
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

        self.add_account_use_case: AddAccountUseCase = AddAccountUseCase(
            self.account_repository,
            self.position_repository
        )
        self.mark_instrument_use_case: MarkInstrumentUseCase = MarkInstrumentUseCase(
            self.account_repository,
            self.instrument_repository,
            self.position_repository
        )
        self.pay_bonus_use_case: PayBonusUseCase = PayBonusUseCase(
            self.account_repository,
            self.position_repository
        )

        self.api_use_case: ApiUseCase = ApiUseCase(
            self.account_repository,
            self.instrument_repository,
            self.position_repository,
            self.trading_repository
        )
    
    def add_account(self, account_id: str, name: str, balance: int = 0) -> int:
        '''
        error codes:
        -1: account_id is already in the game
        '''
        try:
            res: int = self.add_account_use_case.add_account(account_id, name, balance)
            self.conn.commit()
            return res
        except Exception as e:
            self.conn.rollback()
    
    def buy(self, account_id: str, display_order: int, price: int) -> Tuple[int, dict]:
        '''
        error codes:
        -1: account does not exist
        -2: no instrument has this display_order
        -3: is in cross with existing order
        -4: at position limit
        '''
        try:
            res: Tuple[int, dict] = self.buy_use_case.buy(account_id, display_order, price)
            self.conn.commit()
            return res
        except Exception as e:
            print(e)
            self.conn.rollback()
    
    def sell(self, account_id: str, display_order: int, price: int) -> Tuple[int, dict]:
        '''
        error codes are same as self.buy()
        '''
        try:
            res: Tuple[int, dict] = self.sell_use_case.sell(account_id, display_order, price)
            self.conn.commit()
            return res
        except Exception as e:
            print(e)
            self.conn.rollback()
    
    def cancel_buy(self, account_id: str, display_order: int) -> int:
        '''
        error codes:
        -1: account does not exist
        -2: no instrument has this display_order
        -3: no such order to cancel
        '''
        try:
            res: int = self.cancel_use_case.cancel_buy(account_id, display_order)
            self.conn.commit()
            return res
        except Exception as e:
            print(e)
            self.conn.rollback()

    def cancel_sell(self, account_id: str, display_order: int) -> int:
        '''
        error codes are same as self.cancel_buy()
        '''
        try:
            res: int = self.cancel_use_case.cancel_sell(account_id, display_order)
            self.conn.commit()
            return res
        except Exception as e:
            print(e)
            self.conn.rollback()
    
    def mark_occurred(self, display_order: int, did_occur: bool) -> int:
        '''
        error codes:
        -1: no instrument has this display_order
        '''
        try:
            res: int = self.mark_instrument_use_case.mark(display_order, did_occur)
            self.conn.commit()
            return res
        except Exception as e:
            print(e)
            self.conn.rollback()
    
    def pay_bonus(self) -> dict:
        try:
            res: dict = self.pay_bonus_use_case.pay_bonus()
            self.conn.commit()
            return res
        except Exception as e:
            print(e)
            self.conn.rollback()
    
    def get_info(self) -> dict:
        return self.api_use_case.get_info()
    
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

