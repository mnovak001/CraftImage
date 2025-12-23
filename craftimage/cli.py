import argparse
from pathlib import Path

from .context import GenerationConfig, GenerationContext
from .sources import load_source_pools
from .generator import generate_structure
from .diskimage import create_disk_image_from_dir


def parse_counts(count_args):
    result = {}
    if not count_args:
        return result
    for arg in count_args:
        parts = [p.strip() for p in arg.split(",") if p.strip()]
        for part in parts:
            if "=" not in part:
                raise ValueError(f"Invalid --count spec: '{part}'")
            t, n = part.split("=", 1)
            result[t.strip()] = int(n)
    return result


def build_parser():
    p = argparse.ArgumentParser(
        prog="craftimage",
        description="Generate synthetic forensic directory trees and disk images."
    )

    p.add_argument("--sources", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument(
        "--count", action="append",
        metavar="TYPE=N[,TYPE2=N2...]"
    )

    p.add_argument("--max-dirs", type=int, default=20)
    p.add_argument("--max-dir-depth", type=int, default=3)
    p.add_argument("--max-files-per-archive", type=int, default=10)
    p.add_argument("--max-archive-depth", type=int, default=3)
    p.add_argument("--nested-archive-probability", type=float, default=0.3)
    p.add_argument("--seed", type=int, default=None)

    # disk-image options
    p.add_argument("--disk-image", type=Path)
    p.add_argument("--image-size-mb", type=int, default=1024)
    p.add_argument("--filesystem", choices=["ext4", "fat32"], default="ext4")

    return p


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # ---- counts ----
    counts = parse_counts(args.count)
    for t in ["archives", "videos", "images", "documents", "other"]:
        counts.setdefault(t, 0)

    config = GenerationConfig(
        counts=counts,
        max_dirs=args.max_dirs,
        max_dir_depth=args.max_dir_depth,
        max_files_per_archive=args.max_files_per_archive,
        max_archive_depth=args.max_archive_depth,
        nested_archive_probability=args.nested_archive_probability,
        seed=args.seed,
    )

    pools = load_source_pools(args.sources)
    ctx = GenerationContext(config=config, pools=pools)

    print(f"[INFO] Generating structure into {args.output} ...")
    generate_structure(ctx, args.output)
    print("[OK] Directory tree generated.")

    if args.disk_image:
        print("[INFO] Creating disk image...")
        create_disk_image_from_dir(
            source_dir=args.output,
            image_path=args.disk_image,
            size_mb=args.image_size_mb,
            filesystem=args.filesystem,
        )
