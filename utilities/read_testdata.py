import json

class ReadTestData:

    @staticmethod
    def get_search_data():
        with open("test_data/test_data.json") as file:
            data = json.load(file)
            return data["search"]