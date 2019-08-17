import functools
import hashlib as hl

import json
import pickle

from hash_util import hash_block
from block import Block
from transaction import Transaction
from verification import Verification

MINING_REWARD = 10

owner = 'Maciej'
participants = {'Max'}


def load_data():
    global blockchain
    global open_transaction
    try:
        with open('blockchain.txt', mode='r') as f:
            # file_content = pickle.loads(f.read())
            file_content = f.readlines()
            # blockchain = file_content['chain']
            # open_transaction = file_content['ot']
            blockchain = json.loads(file_content[0][:-1])
            updated_blockchain = []
            for block in blockchain:
                converted_tx = [Transaction(
                    tx['sender'],
                    tx['recipient'],
                    tx['amount'])
                    for tx in block['transactions']]
                updated_block = Block(
                    block['index'],
                    block['previous_hash'],
                    converted_tx,
                    block['proof'],
                    block['timestamp'])
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transaction = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transaction:
                updated_transaction = Transaction(
                    tx['sender'], tx['recipient'], tx['amount'])
                updated_transactions.append(updated_transaction)
            open_transaction = updated_transactions
    except (IOError, IndexError):
        genesis_block = Block(0, '', [], 100, 0)
        blockchain = [genesis_block]
        open_transaction = []
    finally:
        print('Cleanup!')


load_data()


def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            print('test', blockchain)
            saveable_chain = [block.__dict__
                              for block in [Block(block_el.index, block_el.previous_hash, [
                                  tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in blockchain]]
            f.write(json.dumps(saveable_chain))
            f.write('\n')
            savable_transactions = [tx.__dict__ for tx in open_transaction]
            f.write(json.dumps(savable_transactions))
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transaction
            # }
            # f.write(pickle.dumps(save_data))
    except IOError:
        print('Saving filed!')


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    verifier = Verification()
    while not verifier.valid_proof(open_transaction, last_hash, proof):
        proof += 1
    return proof


def get_balances(participant):
    tx_sender = [[tx.amount for tx in block.transactions
                  if tx.sender == participant] for block in blockchain]
    open_tx_sender = [tx.amount
                      for tx in open_transaction if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)

    tx_recipient = [[tx.amount for tx in block.transactions
                     if tx.recipient == participant] for block in blockchain]

    amount_received = functools.reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)

    return amount_received - amount_sent


def get_last_blockchain_value():
    """Return last value in blockchain"""
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, amount=1.0, sender=owner):
    transaction = Transaction(sender, recipient, amount)
    verifier = Verification()
    if verifier.verify_transaction(transaction, get_balances):
        open_transaction.append(transaction)
        save_data()
        return True
    return False


def mine_block():
    last_block = blockchain[-1]
    hashed_block = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = Transaction('MINING', owner, MINING_REWARD)
    copied_transaction = open_transaction[:]
    copied_transaction.append(reward_transaction)
    block = Block(len(blockchain), hashed_block, copied_transaction, proof)
    blockchain.append(block)
    return True


def get_user_input():
    tx_recipient = input('Enter the recipient of ther transaction: ')
    tx_amount = float(input('Your transaction amount: '))
    return tx_recipient, tx_amount


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


waiting_for_input = True
while waiting_for_input:
    print('Please choose:')
    print('1: Add new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print('4: Check transactions validity')
    print('q: Quit')

    user_choice = get_user_choice()
    if user_choice == '1':
        recipient, amount = get_user_input()
        if add_transaction(recipient, amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transaction)
    elif user_choice == '2':
        if mine_block():
            open_transaction = []
            save_data()
    elif user_choice == '3':
        for block in blockchain:
            print('Outputting Block')
            print(block)
        else:
            print(20*'-')
    elif user_choice == '4':
        verifier = Verification()
        if verifier.verify_transactions(open_transaction, get_balances):
            print('All transactions are valid!')
        else:
            print('There are invalid transactions!')
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    verifier = Verification()
    if not verifier.verify_chain(blockchain):
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format('Maciej', get_balances('Maciej')))
print('Done!')
