import pytest
import os

@pytest.fixture
def project_root():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
