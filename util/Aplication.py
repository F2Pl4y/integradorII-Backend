from flask import Flask
from flask_cors import CORS
from util.Config import *


class Aplication:

    def __init__(self):
        self.app = Flask(__name__)
        self.app.config['MYSQL_DATABASE_HOST'] = MYSQL_HOST
        self.app.config["MYSQL_DATABASE_PORT"] = MYSQL_PORT
        self.app.config['MYSQL_DATABASE_USER'] = MYSQL_USER
        self.app.config['MYSQL_DATABASE_PASSWORD'] = MYSQL_PASSWORD
        self.app.config['MYSQL_DATABASE_DB'] = MYSQL_DB
        self.cors = CORS(self.app)
