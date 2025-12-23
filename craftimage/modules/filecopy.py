import shutil
from pathlib import Path

from .base import BaseModule
from ..util.fs import safe_mkdir


class FileCopyModule(BaseModule):
    def __init__(self, type_name: str):
        self.type_name = type_name
        self.name = type_name

    def generate(self, ctx, target_dir: Path, depth=0):
        src = ctx.draw_source_file(self.type_name)
        if src is None:
            return None
        safe_mkdir(target_dir)
        dest = target_dir / src.name
        shutil.copy2(src, dest)
        ctx.record_generated(dest, self.type_name)
        return dest
