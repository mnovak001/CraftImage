from pathlib import Path
from typing import Optional, Dict


class BaseModule:
    name: str

    def generate(self, ctx, target_dir: Path, depth: int = 0) -> Optional[Path]:
        raise NotImplementedError


class ModuleRegistry:
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}

    def register(self, module: BaseModule):
        if module.name in self._modules:
            raise ValueError(f"Module '{module.name}' already registered")
        self._modules[module.name] = module

    def all(self):
        return dict(self._modules)

    def get(self, name: str) -> BaseModule:
        return self._modules[name]


MODULES = ModuleRegistry()
