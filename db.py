"""
Certificate Database
----------------------
The single source of truth for every certificate ever issued. This is
what the verification page checks against. It's a plain JSON file --
no server, no database software, no cost -- which is exactly what makes
it possible to host for free on GitHub Pages.

Each department gets its own sequential number, e.g.:
  SPC-ELE-2026-0001, SPC-ELE-2026-0002, ...
  SPC-CON-2026-0001, ...
"""

import json
import os
from datetime import datetime, timezone

DB_PATH = "/home/claude/cert_system/system/database/certificates.json"

DEPT_CODE = {
    "Electronics":            "ELE",
    "Accounting":              "ACC",
    "Garment":                "GAR",
    "GMF (Mechanics)":        "GMF",
    "Automotive":              "AUT",
    "Furniture (Wood Tech)":  "FUR",
    "Construction":            "CON",
}


def _load():
    if not os.path.exists(DB_PATH):
        return {"certificates": []}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(db):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with open(DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)


def next_id(department, year=None):
    """Assigns the next sequential certificate ID for a department."""
    year = year or datetime.now().year
    code = DEPT_CODE.get(department, "GEN")
    db = _load()
    existing = [
        c for c in db["certificates"]
        if c["id"].startswith(f"SPC-{code}-{year}-")
    ]
    n = len(existing) + 1
    return f"SPC-{code}-{year}-{n:04d}"


def register(cert_id, student_name, department, program_level, trade_track, issue_date):
    """Adds a new certificate record. Called automatically at issue time."""
    db = _load()
    # guard against accidental duplicate IDs
    if any(c["id"] == cert_id for c in db["certificates"]):
        raise ValueError(f"Certificate ID {cert_id} already exists in the database.")
    db["certificates"].append({
        "id": cert_id,
        "student_name": student_name,
        "department": department,
        "program_level": program_level,
        "trade_track": trade_track,
        "issue_date": issue_date,
        "issued_at": datetime.now(timezone.utc).isoformat(timespec="seconds") + "Z",
        "status": "valid",
    })
    _save(db)
    return db["certificates"][-1]


def revoke(cert_id, reason=""):
    """Marks a certificate invalid without deleting its history."""
    db = _load()
    for c in db["certificates"]:
        if c["id"] == cert_id:
            c["status"] = "revoked"
            c["revoke_reason"] = reason
            _save(db)
            return c
    raise ValueError(f"Certificate ID {cert_id} not found.")


def lookup(cert_id):
    db = _load()
    for c in db["certificates"]:
        if c["id"] == cert_id:
            return c
    return None
