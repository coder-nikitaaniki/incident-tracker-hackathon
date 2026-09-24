import sqlite3
import os

DB_FILE = "incident_tracker.db"

def get_db_connection():
    try:
        # Check if we need to initialize the schema
        init_needed = not os.path.exists(DB_FILE)
        
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row  # This allows us to access columns by name
        
        if init_needed:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE Incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    severity TEXT NOT NULL CHECK (severity IN ('Low', 'Medium', 'High', 'Critical')),
                    status TEXT NOT NULL DEFAULT 'Open' CHECK (status IN ('Open', 'Investigating', 'Resolved', 'Closed')),
                    reported_by TEXT NOT NULL,
                    assigned_to TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS incident_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                incident_id INTEGER NOT NULL,
                old_status TEXT,
                new_status TEXT NOT NULL,
                actor TEXT NOT NULL,
                changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (incident_id) REFERENCES Incidents(id)
            )
        ''')
        conn.commit()
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
