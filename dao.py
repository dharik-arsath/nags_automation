import json 
class JsonDataDAO:
    def __init__(self):
        pass

    def load_data(self):
        with open("data.json") as f:
            data = json.load(f)
        return data

    def write_data(self, data):
        with open("data.json", "w") as f:
            json.dump(data, f, indent=4)
        return

    def get_raw_data(self) -> dict:
        data = self.load_data()

        return data.get("products", {})

    def get_all_expenses(self) -> list:
        data = self.load_data()
        return data.get("expenses", [])

    def get_drivers(self) -> list:
        data = self.load_data()
        return data.get("drivers", [])

    def add_driver(self, name: str):
        data = self.load_data()
        data["drivers"].append(name)
        self.write_data(data)
        return 


    def get_line(self) -> list:
        data = self.load_data()
        return data.get("line", [])
    
    def remove_product(self, product: str):
        data = self.load_data()
        if product not in data:
            return 
        
        del data[product]
        return 

if __name__ == "__main__":
    data_handler = JsonDataDAO()
    all_p = data_handler.get_raw_data()
    print(all_p)