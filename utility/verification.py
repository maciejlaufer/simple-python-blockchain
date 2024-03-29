from utility.hash_util import hash_string_256, hash_block


class Verification:
    @classmethod
    def verify_chain(cls, blockchain):
        """ Verify the current blockchain and return True if it's valid, False if it's not valid """
        for (index, block) in enumerate(blockchain):
            print(index, block)
            if(index == 0):
                continue
            if block.previous_hash != hash_block(blockchain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                print('Proof of work is invalid')
                return False
        return True

    @classmethod
    def verify_transactions(cls, open_transaction, get_balances):
        """Verifies all open transactions."""
        return all([cls.verify_transaction(tx, get_balances) for tx in open_transaction])

    @staticmethod
    def verify_transaction(transaction, get_balances):
        sender_balance = get_balances()
        return sender_balance >= transaction.amount

    @staticmethod
    def valid_proof(transaction, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transaction]) +
                 str(last_hash) + str(proof)).encode()
        guess_hash = hash_string_256(guess)
        print(guess_hash)
        return guess_hash[0:2] == '00'
