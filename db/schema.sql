-- SQLite schema for Incident Tracker

-- Enforce foreign keys for cascading deletes
PRAGMA foreign_keys = ON;

-- Create Incidents Table
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
);

-- Create Audit Log Table
CREATE TABLE IF NOT EXISTS incident_audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    incident_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT NOT NULL,
    actor TEXT NOT NULL,
    changed_at DATETIME DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),
    FOREIGN KEY (incident_id) REFERENCES Incidents(id) ON DELETE CASCADE
);

-- Add Indexes for performance
CREATE INDEX IF NOT EXISTS idx_incidents_status ON Incidents(status);
CREATE INDEX IF NOT EXISTS idx_incidents_severity ON Incidents(severity);
CREATE INDEX IF NOT EXISTS idx_incidents_assigned_to ON Incidents(assigned_to);
