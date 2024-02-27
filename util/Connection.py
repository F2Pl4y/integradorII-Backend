from flaskext.mysql import MySQL
from util.Aplication import Aplication

class Connection:

    def __init__(self):
        aplication = Aplication()
        self.app = aplication.app
        self.mysql = MySQL(self.app)