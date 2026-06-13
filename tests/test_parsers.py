import pytest
from backend.app.parsers.factory import ParserFactory
from backend.app.models.types import ParseRequest

def test_python_parser():
    factory = ParserFactory()
    parser = factory.get_parser('python')
    assert parser is not None
    
    req = ParseRequest(
        fileId="f1", path="a.py", language="python", content="import os\nfrom sys import path\ndef func(): pass",
        contentHash="h", version=1, projectRoot="/"
    )
    res = parser.parse(req)
    
    assert res.parsed is True
    assert len(res.imports) == 2
    assert res.imports[0].source == "os"
    assert res.imports[1].source == "sys"
    assert len(res.exports) == 1
    assert res.exports[0].name == "func"
    assert res.exports[0].kind == "function"
