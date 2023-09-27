import os
import tempfile
import pytest
import ruamel.yaml
from pathlib import Path
from yamlstore import Document, DocumentDatabase

@pytest.fixture
def temp_yaml_file():
    data = {"key1": "value1", "key2": "value2"}
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".yaml") as temp_file:
        yaml = ruamel.yaml.YAML()
        yaml.dump(data, temp_file)
        yield Path(temp_file.name)
    os.remove(temp_file.name)

def test_document_creation(temp_yaml_file):
    document = Document(temp_yaml_file)
    assert document["key1"] == "value1"


def test_document_db_creation(temp_yaml_file):
    db = DocumentDatabase(temp_yaml_file.parent)
    document = db[temp_yaml_file.stem]
    assert document["key1"] == "value1"

def test_document_db_iteration(temp_yaml_file):
    db = DocumentDatabase(temp_yaml_file.parent)
    docs = list(db)
    assert len(docs) == 1

def test_document_db_document_iteration(temp_yaml_file):
    db = DocumentDatabase(temp_yaml_file.parent)
    document = db[temp_yaml_file.stem]
    keys = list(document)
    assert "key1" in keys
    assert "key2" in keys

if __name__ == "__main__":
    pytest.main()
