import ruamel.yaml
from pathlib import Path

class Document:
    def __init__(self, data, file_path):
        self.data = data
        self.file_path = Path(file_path)
        self.yaml = ruamel.yaml.YAML()

    def sync(self):
        with self.file_path.open("w") as f:
            self.yaml.dump(self.data, f)

    def __getitem__(self, key):
        return self.data.get(key)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.sync()

    def __iter__(self):
        return iter(self.data)


class DocumentDatabase:
    def __init__(self, directory):
        self.directory = Path(directory)
        self.documents = {}
        self.yaml = ruamel.yaml.YAML()

        self.load_documents()

    def load_documents(self):
        for file_path in self.directory.glob("*.yaml"):
            with file_path.open("r") as f:
                data = self.yaml.load(f)
                self.documents[file_path.stem] = Document(data, file_path)

    def __getitem__(self, key):
        return self.documents.get(key)

    def __iter__(self):
        return iter(self.documents.values())
