import json

from dao import JsonDataDAO 
from loguru import logger 

class JsonDataHandler:
    def __init__(self):
        self.data_dao = JsonDataDAO()
        self.logger   = logger 


    def load_data(self):
        with open("data.json") as f:
            data = json.load(f)
        return data

    def get_raw_data(self) -> dict:
        return self.data_dao.get_raw_data()

    def get_all_expenses(self):
        return self.data_dao.get_all_expenses()

    def get_drivers(self):
        return self.data_dao.get_drivers()
    
    def get_line(self):
        return self.data_dao.get_line()

if __name__ == "__main__":
    data_handler = JsonDataHandler()
    all_expenses = data_handler.get_all_expenses()
    data_handler.get_raw_data()