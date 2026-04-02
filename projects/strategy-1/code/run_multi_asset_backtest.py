from __future__ import annotations

import sys
from pathlib import Path

# Reuse shared Team GSD backtesting primitives from the shared module tree.
ROOT = Path(__file__).resolve().parents[3]
SHARED_CODE = ROOT / "code"
if str(SHARED_CODE) not in sys.path:
    sys.path.insert(0, str(SHARED_CODE))

from multi_asset_backtest.pipeline import main


if __name__ == "__main__":
    main()
