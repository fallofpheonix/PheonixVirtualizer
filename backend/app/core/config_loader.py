import os
import yaml
from typing import Optional
from ..models.types import PheonixConfig

class ConfigLoader:
    @staticmethod
    def load_config(project_root: str) -> PheonixConfig:
        config_path = os.path.join(project_root, ".pheonix.yml")
        if not os.path.exists(config_path):
            return PheonixConfig()

        try:
            with open(config_path, 'r') as f:
                data = yaml.safe_load(f)
                if not data:
                    return PheonixConfig()
                return PheonixConfig.model_validate(data)
        except Exception as e:
            print(f"Error loading .pheonix.yml: {e}")
            return PheonixConfig()
