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
        self._modified = False

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

    @property
    def modified(self):
        return self._modified

    def sync(self):
        if self._path:
            with self._path.open("w") as f:
                self._yaml.dump(self.data, f)

    def __setitem__(self, key, value):
        self.data[key] = value
        self._modified = True
        if self._autosync:
            self.sync()

    def __str__(self):
        return self.get("title") or self.get("description") or str(self._path)

    def __repr__(self) -> str:
        return str(self)


class DocumentDatabase(UserDict):

    ITEM = Document

    def __init__(self, directory:Optional[Path]=None, name:Optional[str]=None, autosync:bool=False):
        super().__init__()
        self.directory = directory
        self.name = name
        self._autosync = autosync
        self._modified = False

        # TODO some use cases require multiple directories

        if directory:

            if directory.is_dir():
                self.load_documents(directory)
            elif not directory.exists():
                directory.mkdir()
            else:
                raise ValueError(f"Invalid directory: {directory}")
            self.name = directory.name

        elif name:
            self.directory = Path(name)
            if not self.directory.exists():
                self.directory.mkdir()

    @property
    def modified(self):
        return self._modified

    def load_documents(self, directory:Path):
        if not directory:
            raise ValueError("No directory specified")
        for doc_path in Path(directory).glob("*.yaml"):
            self.data[doc_path.stem] = self.ITEM(Path(doc_path.absolute().as_posix()))
        self._modified = True

    def sync(self):
        for doc in self.data.values():
            doc.sync()

    def __iadd__(self, doc):
        self.data[doc["title"]] = doc
        self._modified = True
        if self._autosync or doc._autosync:
            if not doc._path:
                doc._path = self.directory / f"{doc['title']}.yaml"
            doc.sync()

        return self

    def __str__(self) -> str:
        return f"{self.name} ({len(self.data)})"

    def __repr__(self) -> str:
        return str(self)
