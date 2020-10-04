from entities.side import Side
from entities.transaction import Transaction

from repos.account_repository import IAccountRepository
from repos.instrument_repository import IInstrumentRepository
from repos.position_repository import IPositionRepository
from repos.trading_repository import ITradingRepository
from repos.transaction_repository import ITransactionRepository

class TradingUseCase:
    def __init__(self, account_repository: IAccountRepository, instrument_repository: IInstrumentRepository,
            position_repository: IPositionRepository, trading_repository: ITradingRepository, transaction_repository: ITransactionRepository):

        self.account_repository: IAccountRepository = account_repository
        self.instrument_repository: IInstrumentRepository = instrument_repository
        self.position_repository: IPositionRepository = position_repository
        self.trading_repository: ITradingRepository = trading_repository
        self.transaction_repository: ITransactionRepository = transaction_repository
    
class BuySellUseCase(TradingUseCase):
    def process_transaction(self, transaction: Transaction) -> None:
        if transaction.maker_side == Side.BUY:
            print('%s sold to %s: display_order = %d at %d' %
                (transaction.seller_account.id, transaction.buyer_account.id, transaction.instrument.display_order, transaction.price))
        else:
            print('%s bought from %s: display_order = %d at %d' %
                (transaction.buyer_account.id, transaction.seller_account.id, transaction.instrument.display_order, transaction.price))
        
        self.position_repository.update_account_position_in_instrument(transaction.buyer_account, transaction.instrument, 1)
        self.position_repository.update_account_position_in_instrument(transaction.seller_account, transaction.instrument, -1)
        
        transaction.buyer_account.balance -= transaction.price
        transaction.seller_account.balance += transaction.price
        self.account_repository.increment_account_balance_using_id(transaction.buyer_account.id, -transaction.price)
        self.account_repository.increment_account_balance_using_id(transaction.seller_account.id, transaction.price)

        self.transaction_repository.add_transaction(transaction)