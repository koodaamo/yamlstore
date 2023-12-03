from pathlib import Path
from typing import Union
from io import TextIOWrapper
from .documents import Document, DocumentDatabase


class Configuration(Document):
    "read only document"

    def __setitem__(self, key, value):
        if key in ("title", "description"):
            super().__setitem__(key, value)
        else:
            raise PermissionError("Config is read-only")


class ConfigurationDatabase(DocumentDatabase):
    "configuration database with added root config"

    ITEM = Configuration
