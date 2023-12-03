import ruamel.yaml # type: ignore 
from pathlib import Path
from os import PathLike
from collections import UserDict
from typing import Union, Optional
from io import TextIOWrapper


class Document(UserDict):

    def __init__(self, source:Optional[Path|bytes]=None, title:Optional[str]="", description:Optional[str]="", autosync:bool=False):
        super().__init__()
        self._yaml = ruamel.yaml.YAML(typ='rt')
        self._yaml.default_flow_style = False

        # initiate from path, file, string representing a path,
        # or a tuple with content directly

        if title:
            self.data["title"] = title
        if description:
            self.data["description"] = description

        self._autosync = autosync
        self._path:Optional[Path] = None

        match source:
            case Path():
                self._path = source
                if source.exists():
                    with open(source, "r") as fp:
                        content = fp.read()
                    self.data = self._yaml.load(content)
                    self["title"] = self._path.name[:-5]
                    firstline = content.split("\n", maxsplit=1)[0].strip()
                    self["description"] = firstline.lstrip("# ") if firstline.startswith("#") else ""
            case bytes():
                self._path = None
                self["body"] = source

    def sync(self):
        with self._path.open("w") as f:
            self._yaml.dump(self.data, f)

    def __setitem__(self, key, value):
        self.data[key] = value
        if self._autosync:
            self.sync()

    def __str__(self):
        return self.data["title"]

    def __repr__(self) -> str:
        return str(self)


class DocumentDatabase(UserDict):

    ITEM = Document

    def __init__(self, directory:Optional[Path]=None):
        super().__init__()
        self.directory = directory
        self.name = None

        # TODO some use cases require multiple directories

        if directory:

            if directory.is_dir():
                self.directory = directory
                self.name = self.directory.name
                self.load_documents(self.directory)

            elif not directory.exists():
                directory.mkdir()
            else:
                raise ValueError(f"Invalid directory: {directory}")

    def load_documents(self, directory:Path):
        if not directory:
            raise ValueError("No directory specified")
        for doc_path in Path(directory).glob("*.yaml"):
            self.data[doc_path.stem] = self.ITEM(Path(doc_path.absolute().as_posix()))

    def __iadd__(self, doc):
        self.data[doc["title"]] = doc
        if not doc._path:
            doc._path = self.directory / f"{doc['title']}.yaml"
            doc.sync()
        return self

    def __str__(self) -> str:
        return f"{self.name} ({len(self.data)})"

    def __repr__(self) -> str:
        return str(self)
