import json


class FileOperations:
    @staticmethod
    def load_json(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)

    @staticmethod
    def save_json(file_path, data):
        with open(file_path, 'w') as file:
            file.write(data)
