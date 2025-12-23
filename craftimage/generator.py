from pathlib import Path
from .util.fs import safe_mkdir, create_directory_tree
from .modules import MODULES


def generate_structure(ctx, output_root: Path):
    safe_mkdir(output_root)

    dirs = create_directory_tree(
        output_root,
        ctx.rng,
        max_dirs=ctx.config.max_dirs,
        max_depth=ctx.config.max_dir_depth,
    )

    modules = MODULES.all()

    # ---- archives first ----
    archive_count = ctx.config.counts.get("archives", 0)
    if archive_count > 0 and "archives" in modules:
        mod = modules["archives"]
        for _ in range(archive_count):
            target = ctx.rng.choice(dirs)
            mod.generate(ctx, target, depth=0)

    # ---- simple file types ----
    for type_name in ["videos", "images", "documents", "other"]:
        mod = modules.get(type_name)
        if not mod:
            continue

        # No sources? skip
        if not ctx.pools.as_dict()[type_name]:
            ctx.remaining[type_name] = 0
            continue

        attempts = 0
        max_attempts = ctx.remaining[type_name] * 3

        while ctx.remaining.get(type_name, 0) > 0 and attempts < max_attempts:
            target = ctx.rng.choice(dirs)
            created = mod.generate(ctx, target, depth=0)
            attempts += 1

            if created is None:
                ctx.remaining[type_name] = 0
                break
