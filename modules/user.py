"""create a User Object"""
from modules.database import Database

class User(Database):

    def __init__(self, pseudo="", password="", connected=False, id=""):
        super().__init__()
        self.pseudo = pseudo
        self.password = password
        self.connected = connected
        if self.pseudo:
            self.id = self.get_user_id()

    def get_user_id(self):

        sql='SELECT id FROM user WHERE pseudo = "{}";'.format(self.pseudo)
        self.my_cursor.execute(sql)
        my_result = self.my_cursor.fetchone()
        return my_result[0]

