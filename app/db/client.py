# Code to initilize mongodb client

from pymongo import AsyncMongoClient


## Create an asynchronous MongoDB client
mongo_client = AsyncMongoClient("mongodb://admin:admin@mongo:27017")    #'mongo' is the hostname(name) of the service in docker-compose.yml