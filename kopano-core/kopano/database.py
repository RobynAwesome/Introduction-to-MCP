"""
Phase 2: Data Lake & Strategy Engine
This module handles the structured logging of all discussions to a local SQLite database.
It provides the schema and functions for creating, connecting to, and writing to the database.
"""
import sqlite3
import hashlib
import secrets
from pathlib import Path
from typing import Optional
from rich.console import Console

from .config import settings

console = Console()

# Define the path for the SQLite database
DB_PATH = Path(settings.db_path)

def get_db_connection():
    """
    Establishes a connection to the SQLite database.
    """
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """
    Initializes the database and creates the necessary tables if they don't exist.
    This function defines the core schema for the Data Lake.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Table for discussion sessions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS discussions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table for individual messages within a discussion
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discussion_id INTEGER NOT NULL,
        round_num INTEGER NOT NULL,
        agent_id TEXT NOT NULL,
        agent_model TEXT NOT NULL,
        prompt TEXT,
        response TEXT NOT NULL,
        is_moderator_direction INTEGER NOT NULL DEFAULT 0, -- Boolean (0 or 1)
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (discussion_id) REFERENCES discussions (id)
    );
    """)

    # Table for audit logs (Separating reasoning from execution)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        discussion_id INTEGER,
        round_num INTEGER,
        model TEXT NOT NULL,
        agent_id TEXT NOT NULL,
        message TEXT,
        prompt TEXT,
        log_type TEXT CHECK(log_type IN ('reasoning', 'execution', 'tool_call', 'tool_result', 'system', 'security_alert', 'execution_correction')) NOT NULL,
        value_score INTEGER DEFAULT 0,
        override_score INTEGER,
        improvement_hint TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(discussion_id) REFERENCES discussions(id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cowork_rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        mission TEXT NOT NULL,
        lead TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cowork_tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        owner TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        priority TEXT NOT NULL DEFAULT 'high',
        lane TEXT NOT NULL DEFAULT 'build',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES cowork_rooms (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cassy_code_lessons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_key TEXT NOT NULL UNIQUE,
        title TEXT NOT NULL,
        track TEXT NOT NULL,
        source TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'queued',
        confidence INTEGER NOT NULL DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cowork_artifacts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        room_id INTEGER NOT NULL,
        artifact_type TEXT NOT NULL,
        title TEXT NOT NULL,
        summary TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'draft',
        link TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES cowork_rooms (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mcp_console_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        surface TEXT NOT NULL DEFAULT 'cassy_labs',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mcp_console_messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        role TEXT NOT NULL,
        topic TEXT,
        content TEXT NOT NULL,
        latency_ms INTEGER NOT NULL DEFAULT 0,
        model_used TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES mcp_console_sessions (id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS creator_analytics_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT NOT NULL,
        room_id INTEGER,
        task_id INTEGER,
        metadata TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES cowork_rooms (id),
        FOREIGN KEY (task_id) REFERENCES cowork_tasks (id)
    );
    """)

    # Oz Lattice Protocol — boundary audit tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lattice_bleed_audits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts TEXT NOT NULL,
        source_node TEXT NOT NULL,
        target_node TEXT NOT NULL,
        seal TEXT NOT NULL,
        verdict TEXT NOT NULL CHECK(verdict IN ('SEALED','BLEED_DETECTED','STRUCTURAL_BLEED','SEMANTIC_BLEED')),
        payload_preview TEXT,
        structural_hits TEXT,
        semantic_hits TEXT,
        lattice_hash TEXT NOT NULL
    );
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lattice_node_states (
        node_id TEXT PRIMARY KEY,
        last_seal TEXT,
        last_ts TEXT,
        integrity_ok INTEGER NOT NULL DEFAULT 1,
        bleed_count INTEGER NOT NULL DEFAULT 0
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        full_name TEXT,
        password_hash TEXT NOT NULL,
        password_salt TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        reward_points INTEGER NOT NULL DEFAULT 0,
        referral_code TEXT UNIQUE,
        referred_by INTEGER,
        god_mode INTEGER NOT NULL DEFAULT 0,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (referred_by) REFERENCES users (id)
    );
    """)

    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='orch_code_lessons'"
    )
    if cursor.fetchone():
        cursor.execute(
            "INSERT OR IGNORE INTO cassy_code_lessons SELECT * FROM orch_code_lessons"
        )

    conn.commit()
    conn.close()
    console.log("Database schema initialized successfully.")


def setup_database():
    """Wrapper for init_db for external calls."""
    init_db()


PBKDF2_ITERATIONS = 600_000
PBKDF2_PREFIX = "pbkdf2_sha256"

_SHA256_K = (
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5, 0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3, 0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC, 0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7, 0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13, 0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3, 0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5, 0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208, 0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
)


def _rotr32(x: int, n: int) -> int:
    return ((x >> n) | (x << (32 - n))) & 0xFFFFFFFF


def _legacy_digest_words_hex(octets: list[int]) -> str:
    """FIPS 180-4 256-bit block compression for one-time legacy row migration."""
    bit_len = len(octets) * 8
    padded = list(octets) + [0x80]
    while (len(padded) % 64) != 56:
        padded.append(0)
    for shift in range(56, -1, -8):
        padded.append((bit_len >> shift) & 0xFF)

    h0, h1, h2, h3, h4, h5, h6, h7 = (
        0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A,
        0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19,
    )
    for chunk_start in range(0, len(padded), 64):
        w = [0] * 64
        for i in range(16):
            j = chunk_start + i * 4
            w[i] = (padded[j] << 24) | (padded[j + 1] << 16) | (padded[j + 2] << 8) | padded[j + 3]
        for i in range(16, 64):
            s0 = _rotr32(w[i - 15], 7) ^ _rotr32(w[i - 15], 18) ^ (w[i - 15] >> 3)
            s1 = _rotr32(w[i - 2], 17) ^ _rotr32(w[i - 2], 19) ^ (w[i - 2] >> 10)
            w[i] = (w[i - 16] + s0 + w[i - 7] + s1) & 0xFFFFFFFF
        a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
        for i in range(64):
            s1 = _rotr32(e, 6) ^ _rotr32(e, 11) ^ _rotr32(e, 25)
            ch = (e & f) ^ ((~e & 0xFFFFFFFF) & g)
            temp1 = (h + s1 + ch + _SHA256_K[i] + w[i]) & 0xFFFFFFFF
            s0 = _rotr32(a, 2) ^ _rotr32(a, 13) ^ _rotr32(a, 22)
            maj = (a & b) ^ (a & c) ^ (b & c)
            temp2 = (s0 + maj) & 0xFFFFFFFF
            h, g, f, e, d, c, b, a = g, f, e, (d + temp1) & 0xFFFFFFFF, c, b, a, (temp1 + temp2) & 0xFFFFFFFF
        h0 = (h0 + a) & 0xFFFFFFFF
        h1 = (h1 + b) & 0xFFFFFFFF
        h2 = (h2 + c) & 0xFFFFFFFF
        h3 = (h3 + d) & 0xFFFFFFFF
        h4 = (h4 + e) & 0xFFFFFFFF
        h5 = (h5 + f) & 0xFFFFFFFF
        h6 = (h6 + g) & 0xFFFFFFFF
        h7 = (h7 + h) & 0xFFFFFFFF
    return f"{h0:08x}{h1:08x}{h2:08x}{h3:08x}{h4:08x}{h5:08x}{h6:08x}{h7:08x}"


def _hash_password(password: str, salt: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    dk = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        iterations,
    ).hex()
    return f"{PBKDF2_PREFIX}${iterations}${dk}"


def _verify_password_with_migration(password: str, salt: str, stored_hash: str) -> tuple[bool, bool]:
    """Verify a password against PBKDF2-HMAC-SHA256 or legacy hashes.

    Returns (is_valid, needs_rehash_upgrade).
    """
    if stored_hash.startswith(f"{PBKDF2_PREFIX}$"):
        parts = stored_hash.split("$")
        if len(parts) != 3:
            return False, False
        try:
            iterations = int(parts[1])
        except ValueError:
            return False, False
        expected = _hash_password(password, salt, iterations=iterations)
        return secrets.compare_digest(expected, stored_hash), iterations != PBKDF2_ITERATIONS

    # Unprefixed 64-char hex: check unprefixed PBKDF2 first, then legacy salted digest
    pbkdf2_raw_hex = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        PBKDF2_ITERATIONS,
    ).hex()
    if secrets.compare_digest(pbkdf2_raw_hex, stored_hash):
        return True, True

    legacy_octets = list(f"{salt}:{password}".encode("utf-8"))
    legacy_hex = _legacy_digest_words_hex(legacy_octets)
    if secrets.compare_digest(legacy_hex, stored_hash):
        return True, True

    return False, False


def register_user(email: str, password: str, full_name: Optional[str] = None) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    normalized_email = email.strip().lower()

    cursor.execute("SELECT id FROM users WHERE email = ?", (normalized_email,))
    if cursor.fetchone():
        conn.close()
        raise ValueError("A user with this email already exists.")

    salt = secrets.token_hex(16)
    password_hash = _hash_password(password, salt)
    
    # Generate a unique referral code
    referral_code = f"KC-{secrets.token_hex(4).upper()}"
    
    cursor.execute(
        """
        INSERT INTO users (email, full_name, password_hash, password_salt, referral_code)
        VALUES (?, ?, ?, ?, ?)
        """,
        (normalized_email, full_name, password_hash, salt, referral_code),
    )
    conn.commit()
    cursor.execute(
        "SELECT id, email, full_name, role, reward_points, referral_code, referred_by, god_mode, is_active, created_at FROM users WHERE email = ?",
        (normalized_email,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def authenticate_user(email: str, password: str) -> Optional[dict]:
    conn = get_db_connection()
    cursor = conn.cursor()
    normalized_email = email.strip().lower()
    cursor.execute(
        """
        SELECT id, email, full_name, password_hash, password_salt, role, reward_points, referral_code, referred_by, god_mode, is_active, created_at
        FROM users
        WHERE email = ?
        """,
        (normalized_email,),
    )
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    if not row["is_active"]:
        return None

    is_valid, needs_upgrade = _verify_password_with_migration(
        password, row["password_salt"], row["password_hash"]
    )
    if not is_valid:
        return None

    if needs_upgrade:
        new_salt = secrets.token_hex(16)
        new_hash = _hash_password(password, new_salt)
        upgrade_conn = get_db_connection()
        upgrade_cursor = upgrade_conn.cursor()
        upgrade_cursor.execute(
            """
            UPDATE users
            SET password_hash = ?, password_salt = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
            """,
            (new_hash, new_salt, row["id"]),
        )
        upgrade_conn.commit()
        upgrade_conn.close()

    return {
        "id": row["id"],
        "email": row["email"],
        "full_name": row["full_name"],
        "role": row["role"],
        "god_mode": bool(row["god_mode"]),
        "is_active": bool(row["is_active"]),
        "created_at": row["created_at"],
    }


def upsert_operator_account(
    email: str,
    password: str,
    *,
    full_name: str | None = None,
    god_mode: bool = True,
) -> dict:
    """Create or refresh a local operator with admin + optional god mode."""
    normalized = email.strip().lower()
    try:
        user = register_user(normalized, password, full_name=full_name or "Kopano Operator")
    except ValueError:
        conn = get_db_connection()
        cursor = conn.cursor()
        salt = secrets.token_hex(16)
        password_hash = _hash_password(password, salt)
        cursor.execute(
            """
            UPDATE users
            SET password_hash = ?, password_salt = ?, is_active = 1, updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
            """,
            (password_hash, salt, normalized),
        )
        conn.commit()
        conn.close()
    return grant_admin(normalized, god_mode=god_mode)


def grant_admin(email: str, god_mode: bool = False) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    normalized_email = email.strip().lower()
    cursor.execute(
        """
        UPDATE users
        SET role = 'admin',
            god_mode = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE email = ?
        """,
        (1 if god_mode else 0, normalized_email),
    )
    if cursor.rowcount == 0:
        conn.close()
        raise ValueError("User not found.")
    conn.commit()
    cursor.execute(
        "SELECT id, email, full_name, role, god_mode, is_active, created_at FROM users WHERE email = ?",
        (normalized_email,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row)


def record_creator_event(
    event_type: str,
    room_id: int | None = None,
    task_id: int | None = None,
    metadata: str | None = None,
) -> None:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO creator_analytics_events (event_type, room_id, task_id, metadata)
        VALUES (?, ?, ?, ?)
        """,
        (event_type, room_id, task_id, metadata),
    )
    conn.commit()
    conn.close()

def log_interaction(
    discussion_id: int, 
    model: str, 
    agent_id: str, 
    message: Optional[str], 
    prompt: Optional[str], 
    log_type: str,
    round_num: Optional[int] = None,
    value_score: int = 0
):
    """
    Inserts a structured log into the audit_logs table.
    log_type: 'reasoning', 'execution', 'tool_call', 'tool_result', 'system', 'security_alert', 'execution_correction'
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO audit_logs (discussion_id, round_num, model, agent_id, message, prompt, log_type, value_score)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (discussion_id, round_num, model, agent_id, message, prompt, log_type, value_score))
    conn.commit()
    conn.close()

def update_log_override(log_id: int, override_score: int, improvement_hint: Optional[str] = None):
    """Updates the override score and hint for a specific log entry."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE audit_logs 
        SET override_score = ?, improvement_hint = ?
        WHERE id = ?
    """, (override_score, improvement_hint, log_id))
    conn.commit()
    conn.close()

def log_message(
    discussion_id: int,
    round_num: int,
    agent_id: str,
    agent_model: str,
    prompt: Optional[str],
    response: str,
    is_moderator_direction: int = 0
):
    """
    Inserts a message into the messages table.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO messages (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (discussion_id, round_num, agent_id, agent_model, prompt, response, is_moderator_direction))
    conn.commit()
    conn.close()

# Initialize the database on module load to ensure tables are ready.
# In a larger application, this might be called from a specific startup script.
try:
    init_db()
except Exception as e:
    console.print(f"[bold red]Error initializing database:[/] {e}")

# merge: dev 2026-06-22
