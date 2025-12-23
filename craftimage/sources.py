from pathlib import Path
from .context import SourcePools


def load_source_pools(source_root: Path) -> SourcePools:
    pools = SourcePools()
    mapping = pools.as_dict()

    for type_name in mapping.keys():
        d = source_root / type_name
        if not d.is_dir():
            continue
        files = [p for p in d.rglob("*") if p.is_file()]
        mapping[type_name].extend(files)

    return pools
