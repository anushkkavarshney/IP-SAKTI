"""
Decision Router -- Roadmap.md Section 8.

Also currently missing from the repo (assigned to Member 3), so this is
a small rule-based stand-in living in /backend, same spirit as
classification_stub.py. Swap it out once Member 3 ships real routing.
"""

from typing import Dict


def route(category: str, clarifications: Dict[str, str]) -> Dict:
    biological = clarifications.get("biological_resource") == "yes_biological"
    novel_process = clarifications.get("novel_process") == "yes_novel_process"

    if category == "Cosmetic":
        pathway = "cosmetic"
    elif category == "Nutraceutical":
        pathway = "fssai"
    elif category in ("Classical Ayurvedic Medicine", "Proprietary Ayurvedic Medicine", "Phytopharmaceutical"):
        pathway = "ayush"
    else:
        pathway = "unknown"

    return {
        "category": category,
        "ip_required": novel_process or category == "Phytopharmaceutical",
        "abs_check": biological,
        "regulatory_path": pathway,
        "jurisdiction": "india",
    }
