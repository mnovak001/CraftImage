from pathlib import Path
import subprocess
import shutil
import tempfile
import math

from .util.fs import compute_tree_size_bytes


def _compute_source_size_bytes(source_dir: Path) -> int:
    """
    Compute total size of files under source_dir.

    Prefer `du -sb` (fast, includes sparse-file allocation semantics as reported
    by the platform). Fall back to Python walk if `du` is unavailable.
    """
    try:
        result = subprocess.run(
            ["du", "-sb", str(source_dir)],
            check=True,
            capture_output=True,
            text=True,
        )
        return int(result.stdout.split()[0])
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError, IndexError):
        return compute_tree_size_bytes(source_dir)


def create_disk_image_from_dir(source_dir: Path, image_path: Path, size_mb: int | None, filesystem="ext4"):
    source_dir = source_dir.resolve()
    image_path = image_path.resolve()
    image_path.parent.mkdir(parents=True, exist_ok=True)

    source_size_bytes = _compute_source_size_bytes(source_dir)
    needed_mb = max(1, math.ceil(source_size_bytes / (1024 * 1024) + 50))

    if size_mb is None:
        size_mb = needed_mb
        print(f"[INFO] Computed image size: {size_mb} MB")
    elif size_mb < needed_mb:
        print(f"[WARN] image size too small, recommended at least {needed_mb} MB")

    print(f"[INFO] dd → {image_path}")
    subprocess.run(
        ["dd", "if=/dev/zero", f"of={image_path}", "bs=1M", f"count={size_mb}"],
        check=True
    )

    print(f"[INFO] mkfs.{filesystem}")
    if filesystem.lower() == "ext4":
        subprocess.run(["mkfs.ext4", "-F", str(image_path)], check=True)
    elif filesystem in ("fat32", "vfat"):
        subprocess.run(["mkfs.vfat", str(image_path)], check=True)
    else:
        raise ValueError(f"Unsupported filesystem: {filesystem}")

    mnt = Path(tempfile.mkdtemp(prefix="craftimage-mnt-"))
    try:
        print(f"[INFO] Mounting → {mnt}")
        subprocess.run(["mount", "-o", "loop", str(image_path), str(mnt)], check=True)

        print("[INFO] Copying contents...")
        subprocess.run(["cp", "-a", f"{source_dir}/.", str(mnt)], check=True)

    finally:
        print("[INFO] Unmounting...")
        subprocess.run(["umount", str(mnt)], check=False)
        shutil.rmtree(mnt, ignore_errors=True)

    print(f"[OK] Disk image created: {image_path}")
