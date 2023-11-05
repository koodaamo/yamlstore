import ruamel.yaml
from pathlib import Path
from collections import UserDict
from typing import Union
from io import TextIOWrapper
from itertools import chain


class Document(UserDict):
    def __init__(self, source:Union[TextIOWrapper, str]):

        self.yaml = ruamel.yaml.YAML(typ='rt')
        self.yaml.default_flow_style = False

        if isinstance(source, TextIOWrapper):
            self.path = Path(source.name)
            fp = source
        else:
            self.path = Path(source)
            fp = open(source)

        doc_str = fp.read()
        fp.close()

        self.data = self.yaml.load(doc_str)
        self.name = self.path.name[:-5]
        line = doc_str.split("\n", maxsplit=1)[0].strip()
        self.description = line.lstrip("# ") if line.startswith("#") else ""

    def sync(self):
        with self.path.open("w") as f:
            self.yaml.dump(self.data, f)

    def __setitem__(self, key, value):
        self.data[key] = value
        self.sync()

    def __str__(self):
        return self.name

    def __repr__(self) -> str:
        return str(self)


class Configuration(Document):
    "read only document"

    def __setitem__(self, key, value):
        raise PermissionError("Config is read-only")


class DocumentDatabase(UserDict):

    ITEM = Document

    def __init__(self, directory:str|None=None):
        super().__init__()
        self.directory = None
        self.name = None

        # TODO some use cases require multiple directories

        if directory:
            self.directory = Path(directory)
            self.name = self.directory.name
            self.load_documents()

    def load_documents(self, path:Path|str|None=None):
        directory = path or self.directory
        if not directory:
            raise ValueError("No directory specified")
        for doc_path in Path(directory).glob("*.yaml"):
            self.data[doc_path.stem] = self.ITEM(doc_path.absolute().as_posix())

    def __str__(self) -> str:
        return f"{self.name} ({len(self.data)})"

    def __repr__(self) -> str:
        return str(self)

class ConfigurationDatabase(DocumentDatabase):
    "configuration database with added root config"

    ITEM = Configuration

    def __init__(self, source:Union[TextIOWrapper, str, None]=None):

        if isinstance(source, TextIOWrapper):
            self.data = dict(self.ITEM(source))
        else:
            super().__init__(source)

    def __iadd__(self, filename):
        "add a new configuration document to the database root"
        self._root = self.ITEM(Path(filename))