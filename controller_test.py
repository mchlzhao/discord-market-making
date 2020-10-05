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
            self.position_repository
        )
    
    def add_account(self, account_id: str, name: str, balance: int) -> int:
        return self.add_account_use_case.add_account(account_id, name, balance)
    
    def buy(self, account_id: str, display_order: int, price: int) -> Tuple[int, dict]:
        return self.buy_use_case.buy(account_id, display_order, price)
    
    def sell(self, account_id: str, display_order: int, price: int) -> Tuple[int, dict]:
        return self.sell_use_case.sell(account_id, display_order, price)
    
    def cancel_buy(self, account_id: str, display_order: int) -> int:
        return self.cancel_use_case.cancel_buy(account_id, display_order)

    def cancel_sell(self, account_id: str, display_order: int) -> int:
        return self.cancel_use_case.cancel_sell(account_id, display_order)
    
    def mark_occurred(self, display_order: int, did_occur: bool) -> int:
        return self.mark_instrument_use_case.mark(display_order, did_occur)
    
    def pay_bonus(self) -> None:
        self.pay_bonus_use_case.pay_bonus()
    
    def get_account_info(self) -> dict:
        return self.api_use_case.get_account_info()
    
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

