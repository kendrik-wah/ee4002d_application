import pymongo
from pymongo import MongoClient

class DatabaseClient(object):
	def __init__(self, host='localhost', port=27017):
		self.client = MongoClient(host, port)
	
	def get_client(self):
		return self.client
		
	def get_database(self, db):
		return self.get_client()[db]
		
	def list_databases(self):
		return self.client.list_databases()
	
	def get_collection(self, db, collection):
		return self.get_database(db)[collection]
		
	def list_collections(self, db):
		database = self.get_database(db)
		return database.list_collection_names()
		
	def insert_one_entry(self, db, collection, entry):
		col = self.get_collection(db, collection)
		return col.insert_one(entry)
	
	def find_one_entry(self, db, collection, entry=None):
		col = self.get_collection(db, collection)
		return col.find_one(entry)
		
	def delete_one_entry(self, db, collection, entry):
		col = self.get_collection(db, collection)
		return col.delete_one(entry)
	
	def insert_many_entries(self, db, collection, entries):
		col = self.get_collection(db, collection)
		result = col.insert_many(entries)
		return result
	
	def find_many_entries(self, db, collection, entries=None):
		col = self.get_collection(db, collection)
		result = col.find(entries)
		return result
	
	def delete_many_entries(self, db, collection, entries=None):
		col = self.get_collection(db, collection)
		result = col.delete_many(entries)
		return result
	
