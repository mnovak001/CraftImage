from dataclasses import dataclass, field
from typing import List

TYPES_WITH_CHILDREN = {"dir", "archive"}

@dataclass
class FileTree:
    name: str
    type: str  # "dir", "image", "video", etc.
    children: List["FileTree"] = field(default_factory=list)

    def as_dict(self):
        ret = dict()
        ret["name"] = self.name
        ret["type"] = self.type

        if self.type in TYPES_WITH_CHILDREN:
            ret["children"] = [c.as_dict() for c in self.children]

        return ret