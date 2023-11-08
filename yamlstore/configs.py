from pathlib import Path
from typing import Union
from io import TextIOWrapper
from .documents import Document, DocumentDatabase


class Configuration(Document):
    "read only document"

    def __setitem__(self, key, value):
        raise PermissionError("Config is read-only")


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