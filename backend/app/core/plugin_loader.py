import os
import sys
import importlib.util
from abc import ABC, abstractmethod
from typing import List
from ..models.types import NormalizedGraph, Violation

class BaseRule(ABC):
    @abstractmethod
    def evaluate(self, graph: NormalizedGraph) -> List[Violation]:
        """Evaluate the graph and return a list of violations."""
        pass

def load_plugins(plugins_dir: str) -> List[BaseRule]:
    plugins = []
    if not os.path.exists(plugins_dir):
        return plugins
    
    for filename in os.listdir(plugins_dir):
        if filename.endswith(".py") and not filename.startswith("__"):
            filepath = os.path.join(plugins_dir, filename)
            spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[filename[:-3]] = module
                try:
                    spec.loader.exec_module(module)
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, BaseRule) and attr is not BaseRule:
                            plugins.append(attr())
                except Exception as e:
                    print(f"Failed to load plugin {filename}: {e}")
    return plugins
