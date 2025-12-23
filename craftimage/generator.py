from pathlib import Path
from .util.fs import safe_mkdir, ensure_dir
from .modules import MODULES
from .filetree import FileTree


def generate_structure(ctx, output_root: Path) -> FileTree:
    safe_mkdir(output_root)
    root = FileTree(name=output_root.name, type="dir")

    modules = MODULES.all()

    def random_subpath() -> list[str]:
        depth = ctx.rng.randint(0, ctx.config.max_dir_depth)
        return [f"dir_{ctx.rng.randint(1, 9999)}" for _ in range(depth)]

    # ---- archives first ----
    archive_count = ctx.config.counts.get("archives", 0)
    if archive_count > 0 and "archives" in modules:
        mod = modules["archives"]
        for _ in range(archive_count):
            rel_parts = random_subpath()
            target_path, target_node = ensure_dir(
                output_root, root, rel_parts
            )

            created = mod.generate(ctx, target_path, depth=len(rel_parts))
            if created:
                target_node.children.append(
                    FileTree(name=created.name, type="archive")
                )

    # ---- simple file types ----
    for type_name in ["videos", "images", "documents", "other"]:
        mod = modules.get(type_name)
        if not mod:
            continue

        if not ctx.pools.as_dict().get(type_name):
            ctx.remaining[type_name] = 0
            continue

        attempts = 0
        max_attempts = ctx.remaining.get(type_name, 0) * 3

        while ctx.remaining.get(type_name, 0) > 0 and attempts < max_attempts:
            rel_parts = random_subpath()
            target_path, target_node = ensure_dir(
                output_root, root, rel_parts
            )

            created = mod.generate(ctx, target_path, depth=len(rel_parts))
            attempts += 1

            if created is None:
                ctx.remaining[type_name] = 0
                break

            target_node.children.append(
                FileTree(name=created.name, type=type_name)
            )

    return root