'''
NoSQL Database Implementation
'''

import csv, json, pandas as pd, requests, unittest, uuid

class MangoDB:
    # The MangoDB class should create only the default collection, as shown, on instantiation including a randomly generated uuid using the uuid4()
    def __init__(self):
        self.collections = {}
        self.collections['default'] = { 'version': 1.0,
                                        'db': 'mangodb',
                                        'uuid': str(uuid.uuid4())
                                        }

    # display_all_collections() which iterates through every collection and prints to screen each collection names and the collection's content underneath and may look something like:
    def display_all_collections(self):
        for collection, content in self.collections.items():
            print('collection: ' + collection)
            for key, val in content.items():
                print('     %s: %s' % (key, val))

    # add_collection(collection_name) allows the caller to add a new collection by providing a name. The collection will be empty but will have a name.
    def add_collection(self, collection_name):
        self.collections[collection_name] = {}

    # update_collection(collection_name,updates) allows the caller to insert new items into a collection i.e.
    def update_collection(self, collection_name, updates):
        for key, val in updates.items():
            self.collections[collection_name][key] = val

    # remove_collection() allows caller to delete a specific collection by name and its associated data
    def remove_collection(self, collection_name):
        del(self.collections[collection_name])

    # list_collections() displays a list of all the collections
    def list_collections(self):
        print(self.collections.keys())

    # get_collection_size(collection_name) finds the number of key/value pairs in a given collection
    def get_collection_size(self, collection_name):
        return len(self.collections[collection_name])

    # to_json(collection_name) that converts the collection to a JSON string
    def to_json(self, collection_name):
        return json.dumps(self.collections[collection_name])

    # wipe() that cleans out the db and resets it with just a default collection
    def wipe(self):
        del[self.collections]
        #self.collections = self.__init__()
        self.__init__()

    # get_collection_names() that returns a list of collection names
    def get_collection_names(self):
        return self.collections.keys()

def db_test():
    '''
    Create a class called MangoDB. The MangoDB class wraps a dictionary of dictionaries. At the the root level, each key/value will be called a collection, similar to the terminology used by MongoDB, an inferior version of MangoDB ;) A collection is a series of 2nd level key/value paries. The root value key is the name of the collection and the value is another dictionary containing arbitrary data for that collection.

    For example:

        {
            'default': {
            'version':1.0,
            'db':'mangodb',
            'uuid':'0fd7575d-d331-41b7-9598-33d6c9a1eae3'
            },
        {
            'temperatures': {
                1: 50,
                2: 100,
                3: 120
            }
        }

    The above is a representation of a dictionary of dictionaries. Default and temperatures are dictionaries or collections. The default collection has a series of key/value pairs that make up the collection. The MangoDB class should create only the default collection, as shown, on instantiation including a randomly generated uuid using the uuid4() method and have the following methods:
        - display_all_collections() which iterates through every collection and prints to screen each collection names and the collection's content underneath and may look something like:
            collection: default
                version 1.0
                db mangodb
                uuid 739bd6e8-c458-402d-9f2b-7012594cd741
            collection: temperatures
                1 50
                2 100
        - add_collection(collection_name) allows the caller to add a new collection by providing a name. The collection will be empty but will have a name.
        - update_collection(collection_name,updates) allows the caller to insert new items into a collection i.e.
                db = MangoDB()
                db.add_collection('temperatures')
                db.update_collection('temperatures',{1:50,2:100})
        - remove_collection() allows caller to delete a specific collection by name and its associated data
        - list_collections() displays a list of all the collections
        - get_collection_size(collection_name) finds the number of key/value pairs in a given collection
        - to_json(collection_name) that converts the collection to a JSON string
        - wipe() that cleans out the db and resets it with just a default collection
        - get_collection_names() that returns a list of collection names

	Perform the following:

        - Create an instance of MangoDB
        - Add a collection called testscores
        - Add a collection called testscores
        - Take the test_scores list and insert it into the testscores collection, providing a sequential key i.e 1,2,3...
        - Display the size of the testscores collection
        - Display a list of collections
        - Display the db's UUID
        - Wipe the database clean
        - Display the db's UUID again, confirming it has changed
    '''

    test_scores = [99, 89, 88, 75, 66, 92, 75, 94, 88, 87, 88, 68, 52]

    # Create an instance of MangoDB
    mdb = MangoDB()

    # Add a collection called testscores
    mdb.add_collection('testscores')

    # Take the test_scores list and insert it into the testscores collection, providing a sequential key i.e 1, 2, 3...
    test_scores_dict = dict(zip(range(1,len(test_scores)+1), test_scores))
    mdb.update_collection('testscores', test_scores_dict)

    # Display the size of the testscores collection
    print(mdb.get_collection_size('testscores'))

    # Display the db's UUID
    print(mdb.collections['default']['uuid'])

    # Wipe the database clean
    mdb.wipe()

    # Display the db UUID again, confirming it has changed
    print(mdb.collections['default']['uuid'])

    # Additional test functions

    # Display all the collections and their contents (post-wipe())
    mdb.display_all_collections()

    # Convert default to json
    print(mdb.to_json('default'))


class TestDB(unittest.TestCase):

    def test_exercise02(self):
        print('Testing DB')
        db_test()
        db = MangoDB()
        self.assertEqual(db.get_collection_size('default'), 3)
        self.assertEqual(len(db.get_collection_names()), 1)
        self.assertTrue('default' in db.get_collection_names())
        db.add_collection('temperatures')
        self.assertTrue('temperatures' in db.get_collection_names())
        self.assertEqual(len(db.get_collection_names()), 2)
        db.update_collection('temperatures', {1: 50})
        db.update_collection('temperatures', {2: 100})
        self.assertEqual(db.get_collection_size('temperatures'), 2)
        self.assertTrue(type(db.to_json('temperatures')) is str)
        self.assertEqual(db.to_json('temperatures'), '{"1": 50, "2": 100}')
        db.wipe()
        self.assertEqual(db.get_collection_size('default'), 3)
        self.assertEqual(len(db.get_collection_names()), 1)


if __name__ == '__main__':
    unittest.main()