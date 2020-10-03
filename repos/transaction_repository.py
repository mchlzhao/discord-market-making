from entities.transaction import Transaction

class ITransactionRepository:
    def add_transaction(self, transaction: Transaction) -> None:
        raise NotImplementedError()
