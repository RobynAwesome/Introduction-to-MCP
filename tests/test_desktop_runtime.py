"""Desktop runtime helpers (non-frozen)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "kopano-core"))

from kopano.runtime import configure_frozen_runtime, default_db_path, ensure_desktop_admin, is_frozen_runtime  # noqa: E402


def test_not_frozen_by_default():
    assert is_frozen_runtime() is False
    configure_frozen_runtime()  # no-op when not frozen


def test_default_db_path_under_localappdata():
    path = default_db_path()
    assert path.name == "datalake.db"
    assert path.parent.name == "KopanoContext"


def test_ensure_desktop_admin_creates_admin(tmp_path, monkeypatch):
    import kopano.database as database

    db_file = tmp_path / "datalake.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    monkeypatch.setenv("KOPANO_ADMIN_EMAIL", "admin@kopano.local")
    monkeypatch.setenv("KOPANO_ADMIN_PASSWORD", "demo-admin")

    ensure_desktop_admin()

    from kopano.database import get_db_connection

    conn = get_db_connection()
    row = conn.execute(
        "SELECT email, role FROM users WHERE email = ?",
        ("admin@kopano.local",),
    ).fetchone()
    conn.close()
    assert row is not None
    assert row["role"] == "admin"


def test_ensure_desktop_admin_skips_when_password_unset(tmp_path, monkeypatch):
    import kopano.database as database

    db_file = tmp_path / "datalake.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    monkeypatch.setenv("KOPANO_ADMIN_EMAIL", "admin@kopano.local")
    monkeypatch.delenv("KOPANO_ADMIN_PASSWORD", raising=False)

    ensure_desktop_admin()

    from kopano.database import get_db_connection

    conn = get_db_connection()
    row = conn.execute(
        "SELECT email, role FROM users WHERE email = ?",
        ("admin@kopano.local",),
    ).fetchone()
    conn.close()
    assert row is None


def test_password_hashing_uses_pbkdf2_and_authenticates(tmp_path, monkeypatch):
    import hashlib
    import sqlite3
    import kopano.database as database

    db_file = tmp_path / "datalake.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database.init_db()
    database.register_user("sec@kopano.local", "SovereignPass!2026", full_name="Sec User")

    conn = sqlite3.connect(db_file)
    stored_new = conn.execute(
        "SELECT password_hash FROM users WHERE email = ?", ("sec@kopano.local",)
    ).fetchone()[0]
    conn.close()
    assert stored_new.startswith("pbkdf2_sha256$600000$")

    auth_ok = database.authenticate_user("sec@kopano.local", "SovereignPass!2026")
    auth_bad = database.authenticate_user("sec@kopano.local", "WrongPass")
    assert auth_ok is not None
    assert auth_ok["email"] == "sec@kopano.local"
    assert auth_bad is None


def test_legacy_sha256_password_hash_migrates_to_pbkdf2_on_login(tmp_path, monkeypatch):
    import hashlib
    import sqlite3
    import kopano.database as database

    db_file = tmp_path / "datalake.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)
    database.init_db()

    legacy_salt = "a1b2c3d4e5f60718293a4b5c6d7e8f90"
    legacy_secret = "LegacyOperator#2025"
    legacy_hash = hashlib.sha256(f"{legacy_salt}:{legacy_secret}".encode("utf-8")).hexdigest()
    assert len(legacy_hash) == 64

    conn = sqlite3.connect(db_file)
    conn.execute(
        """
        INSERT INTO users (email, full_name, password_hash, password_salt, role, referral_code)
        VALUES (?, ?, ?, ?, 'admin', 'KC-LEGACY01')
        """,
        ("legacy@kopano.local", "Legacy Admin", legacy_hash, legacy_salt),
    )
    conn.commit()
    conn.close()

    # Wrong password must fail and must NOT upgrade the stored legacy hash
    assert database.authenticate_user("legacy@kopano.local", "WrongPassword") is None
    conn = sqlite3.connect(db_file)
    unchanged_hash = conn.execute(
        "SELECT password_hash FROM users WHERE email = ?", ("legacy@kopano.local",)
    ).fetchone()[0]
    conn.close()
    assert unchanged_hash == legacy_hash

    # Correct password must authenticate and transparently upgrade row to PBKDF2-HMAC-SHA256
    migrated_user = database.authenticate_user("legacy@kopano.local", legacy_secret)
    assert migrated_user is not None
    assert migrated_user["email"] == "legacy@kopano.local"

    conn = sqlite3.connect(db_file)
    upgraded_hash, upgraded_salt = conn.execute(
        "SELECT password_hash, password_salt FROM users WHERE email = ?",
        ("legacy@kopano.local",),
    ).fetchone()
    conn.close()
    assert upgraded_hash.startswith("pbkdf2_sha256$600000$")
    assert upgraded_salt != legacy_salt

    # Subsequent authentication uses the upgraded PBKDF2 hash
    assert database.authenticate_user("legacy@kopano.local", legacy_secret) is not None


