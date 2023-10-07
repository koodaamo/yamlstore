import os
import tempfile
import pytest
import ruamel.yaml
from pathlib import Path
from yamlstore import Document, DocumentDatabase
from yamlstore import Configuration, ConfigurationDatabase

@pytest.fixture
def temp_yaml_file():
    data = {"key1": "value1", "key2": "value2"}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml") as temp_file:
        yaml = ruamel.yaml.YAML()
        yaml.dump(data, temp_file)
        yield Path(temp_file.name)

@pytest.fixture
def temp_yaml_files():
    data1 = {"key1": "value1", "key2": "value2"}
    data2 = {"key3": "value3", "key4": "value4"}
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_file1 = Path(temp_dir) / "file1.yaml"
        with open(temp_file1, "w") as f:
            yaml = ruamel.yaml.YAML()
            yaml.dump(data1, f)
        temp_file2 = Path(temp_dir) / "file2.yaml"
        with open(temp_file2, "w") as f:
            yaml = ruamel.yaml.YAML()
            yaml.dump(data2, f)
        yield temp_dir


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


def test_configuration_creation(temp_yaml_file):
    """
    Test that a Configuration object can be created from a YAML file and that it contains the expected data.
    """
    config_db = ConfigurationDatabase(temp_yaml_file.parent)
    config = config_db[temp_yaml_file.stem]
    assert config["key1"] == "value1"


def test_configuration_db_configuration_iteration(temp_yaml_file):
    """
    Test that a Configuration object can be iterated over and that it returns the expected keys.
    """
    config_db = ConfigurationDatabase(temp_yaml_file.parent)
    config = config_db[temp_yaml_file.stem]
    keys = list(config)
    assert "key1" in keys
    assert "key2" in keys


def test_configuration_readonly(temp_yaml_file):
    """
    Test that a Configuration object cannot be written to if it was created from a read-only file.
    """
    # Create a read-only file
    temp_yaml_file.chmod(0o444)

    # Try to modify the configuration
    config_db = ConfigurationDatabase(temp_yaml_file.parent)
    config = config_db[temp_yaml_file.stem]
    with pytest.raises(PermissionError):
        config["key3"] = "value3"

def test_configuration_db_iteration(temp_yaml_files):
    """
    Test that the ConfigurationDatabase object can be iterated over and that it returns the expected number of configurations.
    """
    db = ConfigurationDatabase()
    db.load_documents(temp_yaml_files)
    configs = list(db)
    assert len(configs) == 2

def test_configuration_db_length(temp_yaml_files):
    """
    Test that the ConfigurationDatabase object returns the expected number of configurations.
    """
    db = ConfigurationDatabase()
    db.load_documents(temp_yaml_files)
    assert len(db) == 2

if __name__ == "__main__":
    pytest.main()
