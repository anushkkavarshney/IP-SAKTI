"""
In-memory report storage.

Roadmap.md Section 31 assigns MongoDB Atlas to Member 6, and no DB
integration exists in the repo yet (no pymongo in requirements.txt).
Rather than adding a new database dependency ourselves (forbidden by
Roadmap.md Section 14 unless the team agrees), we keep reports in memory
for now. This is fine for demo/dev but resets on server restart --
flagged as [OPTIONAL ENHANCEMENT] in the backend README to swap in
MongoDB once Member 6's collections are ready.
"""

import uuid
from typing import Dict, Optional

_reports: Dict[str, dict] = {}


def save(report: dict) -> str:
    session_id = str(uuid.uuid4())
    report["session_id"] = session_id
    _reports[session_id] = report
    return session_id


def get(session_id: str) -> Optional[dict]:
    return _reports.get(session_id)
