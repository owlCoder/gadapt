"""GAdapt research package compatibility: moved legacy Python modules."""
from pathlib import Path as _Path
__path__.append(str(_Path(__file__).resolve().parent / "legacy" / "flat"))
