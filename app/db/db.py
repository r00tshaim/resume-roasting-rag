#create database

from .client import mongo_client

database = mongo_client["full_rag_db"]  # Create or get the database named 'full_rag_db'


