from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd


def to_csv(data: Dict[str, Any], path: Path) -> None:
    df = pd.DataFrame(data.get("missing", []), columns=["missing_keys"])
    df.to_csv(path, index=False)


def to_json(data: Dict[str, Any], path: Path) -> None:
    import json

    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def to_xlsx(data: Dict[str, Any], path: Path) -> None:
    with pd.ExcelWriter(path) as writer:
        pd.DataFrame({"coverage": [data.get("coverage")]}).to_excel(
            writer, sheet_name="Summary", index=False
        )
        pd.DataFrame(data.get("missing", []), columns=["missing_keys"]).to_excel(
            writer, sheet_name="Missing Stories", index=False
        )
