import shutil
import zipfile
from pathlib import Path
import os

from .base import BaseModule
from ..util.fs import safe_mkdir
from ..util.names import random_name


class ArchiveModule(BaseModule):
    name = "archives"

    def generate(self, ctx, target_dir: Path, depth=0):
        safe_mkdir(target_dir)

        archive_name = random_name("archive", ".zip", ctx.rng)
        archive_path = target_dir / archive_name

        tmp = target_dir / (archive_name + "_tmp")
        safe_mkdir(tmp)

        count = ctx.rng.randint(1, ctx.config.max_files_per_archive)

        for _ in range(count):
            if (
                depth < ctx.config.max_archive_depth
                and ctx.rng.random() < ctx.config.nested_archive_probability
            ):
                self.generate(ctx, tmp, depth + 1)
            else:
                t, src = ctx.draw_any_source_file(
                    ["videos", "images", "documents", "other"]
                )
                if src is None:
                    break
                shutil.copy2(src, tmp / src.name)

        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmp):
                root = Path(root)
                for fname in files:
                    fpath = root / fname
                    rel = fpath.relative_to(tmp)
                    zf.write(fpath, rel.as_posix())

        shutil.rmtree(tmp, ignore_errors=True)
        ctx.record_generated(archive_path, "archives")
        return archive_path
