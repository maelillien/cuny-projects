'''
Blockchain Implementation

Below is a simple implementation of a blockchain called PandasChain. This blockchain stores transactions in 
pandas DataFrames (in-memory) and does not write to disk. The following are the components of this chain:

1. Transaction - A transaction is an exchange of Pandas coins between two parties. In the case of our blockchain, a transaction 
consists of:

    - Sender: The name of the party that is sending i.e. "Bob"
    - Receiver: The name of the party that is receiving i.e. "Alice"
    - Value: The float amount of Pandas Coins transferred
    - Timestamp: The datetime the transaction occured
    - Transaction Hash: A SHA-256 hash of the string concatenation of timestamp, sender, receiver, amount a random number between 0 and 99

2. Block - A block holds a pool of transactions in a DataFrame. The maximum a single block can hold is 10 transactions. 
When a block is created, it contains zero transactions and has a status of UNCOMITTED. Once a block contains 10 transactions, 
that block then is marked COMMITTED and a new block is created for future transactions. Blocks are chained together by 
their block hash ID and previous block hash. Each block, except the first genesis block, tracks the hash of the previous block. 
When a block generates its own hash identifier, it uses the previous blocks hash as one of several strings it will concantenate. 

A block consists of:

    - Sequence ID: A unique sequential number starting at 0 that increments by 1 that identifies each block
    
    - Transactions list: A pandas DataFrame containing all of the transactions contained by the block
    
    - Status: Either UNCOMMITTED or COMMITTED
    
    - Merkle Root: A root hash of transactions. In real blockchains like Bitcoin & Ethereum, a 
    Merkle trie (yes, that's spelled trie!) uses a binary tree. We won't do that here. In our case, we will not use 
    a tree but simply take the hash of the string concatenation of all the transaction hashes 
    in a block once a block is full (reaches 10 transactions)
    
    - Block hash: The hash of this block is created by the hash of the string concatenation of the previous block's 
    hash, the chains hash id, current date time, sequence id of the block, a random integer between 0 and 99 and the root Merkle hash. 
    The block hash is generated when a block is full and is committed.

3. PandasChain - A container class that manages all interaction to the internal state of the chain, i.e. users only 
interact with an instance of PandasChain and no other class. A PandasChain class consists of:

    - Name: An arbitrary name of this instance of the chain provided in the constructor when PandasChain is created (see
    test cases for usage examples)
    
    - Chain: A Python list of blocks
    
    - Chain ID: A hash concatenation of a UUID, name of the chain, timestamp of creation of the chain that uniquely
    identifies this chain instance.
    
    - Sequence ID: Tracks the current sequence ID and manages it for new blocks to grab and use
    
    - Previous Hash: Tracks what the previous hash of the just committed block is so that a new block can be instantiated 
    with the previous hash passed into its constructor
    
    - Current block: Which block is current and available to hold incoming transactions

    The only way to interact with a PandasChain instance is via the add_transaction() method that accepts new transactions and 
    methods that print out chain data like display_block_headers(). There should be no other way to reach the underlying
    blocks or pandas DataFrames that hold transactions.

'''


import datetime as dt
import hashlib
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import unittest
import uuid
import random

class PandasChain:

    def __init__(self, name): 
        self.__name = name.upper() # Convert name to upper case and store it here
        self.__chain = [] # Create an empty list
        self.__id = hashlib.sha256(str(str(uuid.uuid4())+self.__name+str(dt.datetime.now())).encode('utf-8')).hexdigest()
        self.__seq_id = 0 # Create a sequence ID and set to zero
        self.__prev_hash = None # Set to None
        self.__current_block = Block(self.__seq_id, self.__prev_hash) # Create a new Block
        print(self.__name,'PandasChain created with ID',self.__id,'chain started.')
    
    # Loop through all committed and uncommitted blocks and display all transactions in them
    def display_chain(self): 
        for block in self.__chain:
            block.display_transactions()
    
    # This method accepts a new transaction and adds it to current block if block is not full. 
    # If block is full, it will delegate the committing and creation of a new current block 
    def add_transaction(self,s,r,v): 
        if self.__current_block.get_size() >= 10:
            self.__commit_block(self.__current_block)
        self.__current_block.add_transaction(s,r,v)
    
    # This method is called by add_transaction if a block is full (i.e 10 or more transactions). 
    # It is private and therefore not public accessible. It will change the block status to committed, obtain the merkle
    # root hash, generate and set the block's hash, set the prev_hash to the previous block's hash, append this block 
    # to the chain list, increment the seq_id and create a new block as the current block
    def __commit_block(self,block): 
        # Add code here
        block.set_status("COMMITTED") # Change the block status to committed

        merkle_root = block.get_simple_merkle_root() # Obtain the merkle root hash

        # Generate and set the block's hash: hash of the string concatenation of the previous block's hash, the chains hash id,
        # current date time, sequence id of the block, a random integer between 0 and 99 and the root Merkle hash
        block_hash = hashlib.sha256(str(''.join([str(self.__prev_hash),
                                                    str(self.__id),
                                                    str(dt.datetime.now()),
                                                    str(self.__seq_id),
                                                    str(random.randint(0,99)),
                                                    str(merkle_root)])).encode('utf-8')).hexdigest()
        block.set_block_hash(block_hash)
        self.__prev_hash = block_hash #  Set the prev_hash to the previous block's hash
        self.__chain.append(block) # Append this block to the chain list
        print('Block committed')

        self.__seq_id += 1 # Increment the seq_id
        self.__current_block = Block(self.__seq_id, self.__prev_hash) # Create new block as current block

    
    # Display just the metadata of all blocks (committed or uncommitted), one block per line.  
    # You'll display the sequence Id, status, block hash, previous block's hash, merkle hash and total number (count) 
    # of transactions in the block
    def display_block_headers(self):
        for block in self.__chain:
            block.display_header()
    
    # Return int total number of blocks in this chain (committed and uncommitted blocks combined)
    def get_number_of_blocks(self):
        # Block ids start at 0
        return self.__seq_id+1

    # Returns all of the values (Pandas coins transferred) of all transactions from every block as a single list
    def get_values(self):
        values = []
        for block in self.__chain:
            values.append(block.get_values())

        # On Slack, it was questioned whether transactions in a current block (but not in the chain) should be returned.
        # I am providing that functionality here.
        values_current = self.__current_block.get_values()
        values.append(values_current)

        values = [item for sublist in values for item in sublist] # Flatten list of lists into a single list

        return values

    # Returns all of the values of all transactions from every block as a DataFrame and then plot them
    def get_values_modified(self):
        values = pd.DataFrame(columns=['Timestamp','Value'])
        for block in self.__chain:
            values = values.append(block.get_values_modified(), ignore_index=True)

        values_current = self.__current_block.get_values_modified()
        values = values.append(values_current, ignore_index=True)

        N = len(values.index)
        ind = np.arange(N)  # the evenly spaced plot indices for x-axis
        # Set x-axis limits
        xmin = -0.75
        xmax = N-0.25

        # Define formatting functions for plotting
        def major_formatter(x, pos):
            return "%d" % x

        def date_formatter(x, pos=None):
            thisind = np.clip(int(x + 0.5), 0, N - 1)
            return values['Timestamp'][thisind].strftime('%x %H:%M:%S.%f')[:-3]

        fig, axes = plt.subplots(nrows=2, figsize=(9, 7)) # Create two subplots

        # Plot transactions by index
        ax = axes[0]
        ax.bar(ind, values['Value'])
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(major_formatter))
        ax.set_xlim([xmin, xmax])
        ax.set_ylabel('Value (PandaCoins)')
        ax.set_title("Transaction by Index", fontsize=20)

        ax = axes[1]
        ax.bar(ind, values['Value'])

        # Plot transactions by timestamp
        ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
        ax.xaxis.set_major_formatter(ticker.FuncFormatter(date_formatter))
        ax.set_xlim([xmin, xmax])
        ax.tick_params(labelrotation=90)
        ax.set_ylabel('Value (PandaCoins)')
        ax.set_title("Transaction by Timestamp", fontsize=20)

        plt.tight_layout(h_pad=5.0)
        # Un-comment the below if the plot should be display from the function instead of from the caller level
        #plt.show()

        return values, plt
        ## -------------------------------------
            
class Block:

    def __init__(self,seq_id,prev_hash): 
        self.__seq_id = seq_id
        self.__prev_hash = prev_hash
        self.__col_names = ['Timestamp','Sender','Receiver','Value','TxHash']
        self.__transactions = pd.DataFrame(columns=self.__col_names) # Create a new blank DataFrame with set headers
        self.__status = 'UNCOMMITED' # Initial status. This will be a string.
        self.__block_hash = None
        self.__merkle_tx_hash = None
        
    # Display on a single line the metadata of this block. You'll display the sequence Id, status, 
    # block hash, previous block's hash, merkle hash and number of transactions in the block
    def display_header(self): 
        print(' '.join(str(elem) for elem in [  self.__seq_id,
                                                self.__status,
                                                self.__block_hash,
                                                self.__prev_hash,
                                                self.__merkle_tx_hash,
                                                len(self.__transactions.index)
                                                ]))
    
    # This is the interface for how transactions are added
    def add_transaction(self,s,r,v): 
        ts = dt.datetime.now() # Get current timestamp
        tx_hash = hashlib.sha256(str(''.join([str(elem) for elem in [ts, s, r, v]])).encode('utf-8')).hexdigest()  # Hash of timestamp, sender, receiver, value

        new_transaction = pd.DataFrame([[ts, s, r, v, tx_hash]], columns=self.__col_names) # Create DataFrame with transaction data (a DataFrame with only 1 row)
        # Append to the transactions data
        print('adding new transaction')
        self.__transactions = self.__transactions.append(new_transaction, ignore_index=True)
        
    # Print all transactions contained by this block
    def display_transactions(self):
        print(self.__transactions)
    
    # Return the number of transactions contained by this block
    def get_size(self): 
        return len(self.__transactions.index)
    
    # Setter for status - Allow for the change of status (only two statuses exist - COMMITTED or UNCOMMITTED). There is no need to validate status.
    def set_status(self,status):
        self.__status = status
    
    # Setter for block hash
    def set_block_hash(self,hash):
        self.__block_hash = hash
    
    # Return and calculate merkle hash by taking all transaction hashes, concatenate them into one string and
    # hash that string producing a "merkle root" - Note, this is not how merkle tries work but is instructive 
    # and indicative in terms of the intent and purpose of merkle tries
    def get_simple_merkle_root(self):
        concathash = ''.join(self.__transactions['TxHash'].tolist()) # Contatenate every transaction hash
        merkle_root = hashlib.sha256(concathash.encode('utf-8')).hexdigest() # Compute merkle root hash
        self.__merkle_tx_hash = merkle_root # Set block merkle root hash
        return merkle_root

    # Returns a list of the values (Pandas coins transferred) contained in the block
    # Modified to return a dict instead, which will be flattened into a list at the caller level
    def get_values(self):
        values = self.__transactions['Value'].tolist()
        return values

    # Returns a DataFrame containing the timestamp and the values contained in the block
    def get_values_modified(self):
        return self.__transactions[['Timestamp','Value']]


class TestBlockchain(unittest.TestCase):
    def test_chain(self):
        block = Block(1,"test")
        self.assertEqual(block.get_size(),0)
        block.add_transaction("Bob","Alice",50)
        self.assertEqual(block.get_size(),1)
        pandas_chain = PandasChain('testnet')
        self.assertEqual(pandas_chain.get_number_of_blocks(),1)
        pandas_chain.add_transaction("Bob","Alice",50)
        pandas_chain.add_transaction("Bob","Alice",51)
        pandas_chain.add_transaction("Bob","Alice",52)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        self.assertEqual(pandas_chain.get_number_of_blocks(),2)
        pandas_chain.add_transaction("Bob","Alice",50)
        pandas_chain.add_transaction("Bob","Alice",51)
        pandas_chain.add_transaction("Bob","Alice",52)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        pandas_chain.add_transaction("Bob","Alice",53)
        self.assertEqual(pandas_chain.get_number_of_blocks(),3)


        # Returns a list of transactions
        values = pandas_chain.get_values()
        print(values)

        # Returns a list of transactions with timestamps, as well a plots of the transactions
        values_m, plot = pandas_chain.get_values_modified()
        print(values_m)
        plot.show()


if __name__ == '__main__':
    unittest.main()
