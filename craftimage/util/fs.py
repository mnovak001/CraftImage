from pathlib import Path
import os
from ..filetree import FileTree


def safe_mkdir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def compute_tree_size_bytes(root: Path) -> int:
    total = 0
    for p in root.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return total


def create_directory_tree(root: Path, rng, max_dirs: int, max_depth: int):
    safe_mkdir(root)
    dirs = [root]

    from .names import random_name

    while len(dirs) < max_dirs:
        parent = rng.choice(dirs)
        depth = len(parent.relative_to(root).parts)
        if depth >= max_depth:
            continue

        new_dir = parent / random_name("dir", "", rng)
        if new_dir.exists():
            continue

        safe_mkdir(new_dir)
        dirs.append(new_dir)

    return dirs

def ensure_dir(
    root_path: Path,
    root_node: FileTree,
    rel_parts: list[str],
) -> tuple[Path, FileTree]:
    """
    Create directories only as needed and mirror them into FileTree.
    """
    path = root_path
    node = root_node

    for part in rel_parts:
        path = path / part
        safe_mkdir(path)

        existing = next(
            (c for c in node.children if c.type == "dir" and c.name == part),
            None,
        )
        if existing:
            node = existing
        else:
            new = FileTree(name=part, type="dir")
            node.children.append(new)
            node = new

    return path, node
