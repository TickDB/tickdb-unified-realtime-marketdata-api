"""Small encrypted SQLite store; transactions serialize one-time credential consumption."""

import hashlib
import json
import os
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

from cryptography.fernet import Fernet


def digest(value: str) -> str:
    return hashlib.sha256(value.encode()).hexdigest()


class Store:
    def __init__(self, path: str, encryption_key: str, resource: str):
        self.cipher = Fernet(encryption_key.encode())
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(self.path, os.O_CREAT | os.O_RDWR, 0o600)
        os.close(fd)
        os.chmod(self.path, 0o600)
        with self.transaction() as db:
            db.execute("CREATE TABLE IF NOT EXISTS records "
                       "(kind TEXT, id TEXT, payload BLOB, expires REAL, family TEXT, "
                       "PRIMARY KEY(kind,id))")
            db.execute("CREATE INDEX IF NOT EXISTS records_family ON records(family)")
            # Detect wrong encryption keys / resource changes before serving traffic.
            meta = self.read(db, "meta", "config")
            if meta is None:
                self.put(db, "meta", "config", {"resource": resource}, 0)
            elif meta["resource"] != resource:
                raise ValueError("OAuth database belongs to a different public resource URL")

    @contextmanager
    def transaction(self):
        db = sqlite3.connect(self.path, timeout=5)
        db.row_factory = sqlite3.Row
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.commit()
        except BaseException:
            db.rollback()
            raise
        finally:
            db.close()

    def read(self, db, kind: str, identifier: str):
        row = db.execute("SELECT payload, expires FROM records WHERE kind=? AND id=?",
                         (kind, identifier)).fetchone()
        if row is None or (row["expires"] and row["expires"] <= time.time()):
            return None
        return json.loads(self.cipher.decrypt(row["payload"]))

    def put(self, db, kind: str, identifier: str, data: dict, expires: float, family=""):
        payload = self.cipher.encrypt(json.dumps(data).encode())
        db.execute("INSERT OR REPLACE INTO records VALUES(?,?,?,?,?)",
                   (kind, identifier, payload, expires, family))

    def delete(self, db, kind: str, identifier: str):
        db.execute("DELETE FROM records WHERE kind=? AND id=?", (kind, identifier))

    def revoke(self, db, family: str):
        db.execute("DELETE FROM records WHERE family=?", (family,))

    def prune(self, db):
        db.execute("DELETE FROM records WHERE expires > 0 AND expires <= ?", (time.time(),))
