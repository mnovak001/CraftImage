from .base import MODULES
from .archives import ArchiveModule
from .filecopy import FileCopyModule

# Register modules
MODULES.register(ArchiveModule())
MODULES.register(FileCopyModule("videos"))
MODULES.register(FileCopyModule("images"))
MODULES.register(FileCopyModule("documents"))
MODULES.register(FileCopyModule("other"))

__all__ = ["MODULES"]
