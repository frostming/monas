from monas.metadata.base import Metadata
from monas.metadata.pep621 import PEP621Metadata
from monas.metadata.setupcfg import SetupCfgMetadata

ALL_METADATA_CLASSES = [PEP621Metadata, SetupCfgMetadata]

__all__ = ["Metadata", "ALL_METADATA_CLASSES"]
