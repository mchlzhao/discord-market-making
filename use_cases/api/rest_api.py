import json

from typing import List, Tuple

from entities.account import Account
from entities.instrument import Instrument
from entities.order import Order

from repos.account_repository import IAccountRepository
from repos.instrument_repository import IInstrumentRepository
from repos.position_repository import IPositionRepository
from repos.trading_repository import ITradingRepository

import settings

class ApiUseCase:
    def __init__(self, account_repository: IAccountRepository, instrument_repository: IInstrumentRepository,
            position_repository: IPositionRepository, trading_repository: ITradingRepository):

        self.account_repository: IAccountRepository = account_repository
        self.instrument_repository: IInstrumentRepository = instrument_repository
        self.position_repository: IPositionRepository = position_repository
        self.trading_repository: ITradingRepository = trading_repository
    
    def get_info(self) -> dict:
        accounts: List[Account] = self.account_repository.get_all_accounts()
        instruments: List[Instrument] = self.instrument_repository.get_all_instruments()
        response: dict = {'accounts': [], 'instruments': []}

        total_pos: dict = {t[0]: t[1] for t in
            self.position_repository.get_total_positions_in_active_instruments() }

        for account in accounts:
            positions_dict: dict = {t[0]: t[1] for t in 
                self.position_repository.get_all_positions_by_account(account)}

            response['accounts'].append({
                'id': account.id,
                'name': account.name,
                'balance': account.balance,
                'weekly_balance': account.balance - self.account_repository.get_weekly_balance(account.id, settings.WEEK_NUMBER-1),
                'total_positions': total_pos[account.id],
                'positions': positions_dict
            })
        
        for instrument in instruments:
            buy_orders: List[Order] = self.trading_repository.get_best_buy_using_instrument_id(instrument.id)
            sell_orders: List[Order] = self.trading_repository.get_best_sell_using_instrument_id(instrument.id)

            buy_orders_response: List[dict] = []
            for order in buy_orders:
                account: Account = self.account_repository.get_account_using_id(order.account_id)
                buy_orders_response.append({
                    'name': account.name,
                    'price': order.price
                })
            sell_orders_response: List[dict] = []
            for order in sell_orders:
                account: Account = self.account_repository.get_account_using_id(order.account_id)
                sell_orders_response.append({
                    'name': account.name,
                    'price': order.price
                })

            response['instruments'].append({
                'id': instrument.id,
                'display_order': instrument.display_order,
                'desc': self.instrument_repository.get_description_using_type_id(instrument.type_id),
                'did_occur': instrument.did_occur,
                'buy_orders': buy_orders_response,
                'sell_orders': sell_orders_response
            })
        
        
        return response
