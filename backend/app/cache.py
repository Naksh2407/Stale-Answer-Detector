import hashlib, json, sqlite3
from .config import settings

_conn = sqlite3.connect(settings.cache_path, check_same_thread=False)
_conn.execute("CREATE TABLE IF NOT EXISTS kv (ns TEXT, key TEXT, value TEXT, PRIMARY KEY (ns, key))")
_conn.commit()

def _key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()

def get(ns: str, raw_key: str):
    row = _conn.execute("SELECT value FROM kv WHERE ns=? AND key=?", (ns, _key(raw_key))).fetchone()
    return json.loads(row[0]) if row else None

def set(ns: str, raw_key: str, value) -> None:
    _conn.execute(
        "INSERT OR REPLACE INTO kv (ns, key, value) VALUES (?, ?, ?)",
        (ns, _key(raw_key), json.dumps(value)),
    )
    _conn.commit()
