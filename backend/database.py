import sqlite3
import os

DB_FILE = os.getenv("DB_FILE", "incident_tracker.db")

def get_db_connection():
    try:
        conn = sqlite3.connect(DB_FILE, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        
        # Enforce foreign keys for cascading deletes
        conn.execute("PRAGMA foreign_keys = ON;")
        
        # Create tables if not exists
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL CHECK(length(title) <= 200),
                description TEXT,
                severity TEXT NOT NULL CHECK(severity IN ('Critical', 'High', 'Medium', 'Low')),
                status TEXT NOT NULL DEFAULT 'Open' CHECK(status IN ('Open', 'Investigating', 'Resolved', 'Closed')),
                reported_by TEXT NOT NULL,
                assigned_to TEXT,
                created_at DATETIME DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                updated_at DATETIME DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incident_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                actor TEXT NOT NULL,
                changed_at DATETIME DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
                FOREIGN KEY (incident_id) REFERENCES Incidents(id) ON DELETE CASCADE
            )
        ''')
        conn.commit()
        
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
