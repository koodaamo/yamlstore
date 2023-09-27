import ruamel.yaml
from pathlib import Path

class Document:
    def __init__(self, docpath):
        self.path = docpath
        self.yaml = ruamel.yaml.YAML(typ='rt')
        self.yaml.default_flow_style = False
        self.data = self.yaml.load(self.path)

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
        self.name = self.directory.name
        self.documents = {}
        self.load_documents()

    def load_documents(self):
        for docpath in self.directory.glob("*.yaml"):
            self.documents[docpath.stem] = Document(docpath)

    def __getitem__(self, key):
        return self.documents.get(key)

    def __iter__(self):
        return iter(self.documents.values())

    def __len__(self):
        return len(self.documents)
