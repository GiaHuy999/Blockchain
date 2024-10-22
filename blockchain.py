import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, transactions, difficulty=2):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.previous_hash = previous_hash
        self.nonce = 0
        self.difficulty = difficulty
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = str(self.index) + str(self.timestamp) + str(self.transactions) + self.previous_hash + str(self.nonce)
        return hashlib.sha256(block_data.encode()).hexdigest()

    def mine_block(self):
        while self.hash[:self.difficulty] != "0" * self.difficulty:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
    
    def create_genesis_block(self):
        return Block(0, "0", "Genesis Block")
    
    def get_last_block(self):
        return self.chain[-1]
    
    def add_block(self, transactions):
        last_block = self.get_last_block()
        new_block = Block(len(self.chain), last_block.hash, transactions)
        new_block.mine_block()
        self.chain.append(new_block)
