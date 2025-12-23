import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

# -----------------------------------------------
# SOURCE POOLS
# -----------------------------------------------

@dataclass
class SourcePools:
    archives: List[Path] = field(default_factory=list)
    videos: List[Path] = field(default_factory=list)
    images: List[Path] = field(default_factory=list)
    documents: List[Path] = field(default_factory=list)
    other: List[Path] = field(default_factory=list)

    def as_dict(self):
        return {
            "archives": self.archives,
            "videos": self.videos,
            "images": self.images,
            "documents": self.documents,
            "other": self.other,
        }


# -----------------------------------------------
# CONFIG
# -----------------------------------------------

@dataclass
class GenerationConfig:
    counts: Dict[str, int]
    max_dirs: int = 20
    max_dir_depth: int = 3
    max_files_per_archive: int = 10
    max_archive_depth: int = 3
    nested_archive_probability: float = 0.3
    seed: Optional[int] = None


# -----------------------------------------------
# CONTEXT OBJECT
# -----------------------------------------------

@dataclass
class GenerationContext:
    config: GenerationConfig
    pools: SourcePools
    rng: random.Random = field(default_factory=random.Random)
    remaining: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        if self.config.seed is not None:
            self.rng.seed(self.config.seed)
        self.remaining = dict(self.config.counts)

    def draw_source_file(self, type_name: str):
        pool = self.pools.as_dict().get(type_name, [])
        if not pool:
            return None
        remaining = self.remaining.get(type_name, 0)
        if remaining <= 0:
            return None
        self.remaining[type_name] = remaining - 1
        return self.rng.choice(pool)

    def draw_any_source_file(self, allowed_types=None):
        pools = self.pools.as_dict()
        if allowed_types is None:
            allowed_types = pools.keys()
        candidates = [
            t for t in allowed_types
            if self.remaining.get(t, 0) > 0 and pools.get(t)
        ]
        if not candidates:
            return None, None
        t = self.rng.choice(candidates)
        return t, self.draw_source_file(t)
