from pymongo import MongoClient
from decouple import config

class MongoDBConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    def __init__(self):
        if self.__initialized:
            return
        self.uri = config("MONGO_URI")
        self.db_name = config("MONGO_DB_NAME")
        self.user_collection_name = config("USER_COLLECTION_NAME")
        self.pdf_data_collection_name = config("PDF_DATA_COLLECTION_NAME")
        self.user_pdf_mapping_collection_name = config("USER_PDF_COLLECTION_NAME")

        self.client = None
        self.db = None
        self.users_collection = None
        self.pdf_data_collection = None
        self.user_pdf_mapping_collection = None

        self.connect()
        self.__initialized = True

    def connect(self):
        try:
            self.client = MongoClient(self.uri)
            self.db = self.client[self.db_name]
            self.users_collection = self.db[self.user_collection_name]
            self.pdf_data_collection = self.db[self.pdf_data_collection_name]
            self.user_pdf_mapping_collection = self.db[self.user_pdf_mapping_collection_name]
            print("Successfully connected to MongoDB")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")

    def get_db(self):
        return self.db

    def get_users_collection(self):
        return self.users_collection

    def get_pdf_data_collection(self):
        return self.pdf_data_collection

    def get_user_pdf_mapping_collection(self):
        return self.user_pdf_mapping_collection

    def close(self):
        if self.client:
            self.client.close()
            print("MongoDB connection closed")
