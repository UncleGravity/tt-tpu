import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
INFO_YAML = REPO_ROOT / "info.yaml"
RTL_DIR = REPO_ROOT / "src/rtl"


def chip_top_module() -> str:
    """Parse the chip's top module name from info.yaml.

    Only useful for tests whose DUT is the chip top. Tests targeting
    individual submodules should name their own DUT directly.
    """
    m = re.search(r'^\s*top_module:\s*"([^"]+)"', INFO_YAML.read_text(), re.MULTILINE)
    if not m:
        raise RuntimeError(f"top_module not found in {INFO_YAML}")
    return m.group(1)
