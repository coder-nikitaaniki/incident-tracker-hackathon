from fastapi import FastAPI, HTTPException, status, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from schemas import IncidentCreate, IncidentUpdate, IncidentStatusUpdate, IncidentOut
from database import get_db_connection

app = FastAPI(title="Incident Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def row_to_dict(cursor, row):
    if not row:
        return None
    return dict(row)

@app.post("/incidents", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_incident(incident: IncidentCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    query = """
    INSERT INTO Incidents (title, description, severity, status, reported_by)
    VALUES (?, ?, ?, 'Open', ?)
    RETURNING *
    """
    try:
        cursor.execute(query, (incident.title, incident.description, incident.severity, incident.reported_by))
        row = cursor.fetchone()
        conn.commit()
        
        created_incident = row_to_dict(cursor, row)
        
        cursor.execute('''
            INSERT INTO incident_audit_log (incident_id, old_status, new_status, actor)
            VALUES (?, NULL, 'Open', ?)
        ''', (created_incident['id'], incident.reported_by))
        conn.commit()
        
        return {
            "success": True,
            "data": created_incident
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/incidents", response_model=List[IncidentOut])
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", pattern="^(created_at|severity)$"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$")
):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    query = "SELECT * FROM Incidents WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if severity:
        query += " AND severity = ?"
        params.append(severity)
    if assigned_to:
        query += " AND assigned_to = ?"
        params.append(assigned_to)
        
    order_col = "created_at" if sort_by == "created_at" else "severity"
    order_dir = "ASC" if order.lower() == "asc" else "DESC"
    query += f" ORDER BY {order_col} {order_dir}"
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        incidents = [row_to_dict(cursor, row) for row in rows]
        return incidents
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/incidents/{incident_id}", response_model=IncidentOut)
def get_incident(incident_id: int = Path(...)):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    query = "SELECT * FROM Incidents WHERE id = ?"
    try:
        cursor.execute(query, (incident_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Incident not found")
        return row_to_dict(cursor, row)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.put("/incidents/{incident_id}", response_model=dict)
def update_incident(incident_id: int, incident: IncidentUpdate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("SELECT id FROM Incidents WHERE id = ?", (incident_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")
        
    update_fields = []
    params = []
    if incident.title is not None:
        update_fields.append("title = ?")
        params.append(incident.title)
    if incident.description is not None:
        update_fields.append("description = ?")
        params.append(incident.description)
    if incident.severity is not None:
        update_fields.append("severity = ?")
        params.append(incident.severity)
    if incident.assigned_to is not None:
        update_fields.append("assigned_to = ?")
        params.append(incident.assigned_to)
        
    if not update_fields:
        conn.close()
        return {"success": True, "message": "No fields to update"}
        
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    
    query = f"UPDATE Incidents SET {', '.join(update_fields)} WHERE id = ?"
    params.append(incident_id)
    
    try:
        cursor.execute(query, params)
        conn.commit()
        return {"success": True, "message": "Incident updated"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.patch("/incidents/{incident_id}/status", response_model=dict)
def update_status(incident_id: int, status_update: IncidentStatusUpdate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    cursor.execute("SELECT status FROM Incidents WHERE id = ?", (incident_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")
        
    current_status = row[0]
    new_status = status_update.status
    
    valid_transitions = {
        "Open": ["Investigating"],
        "Investigating": ["Resolved"],
        "Resolved": ["Closed"],
        "Closed": []
    }
    
    if new_status not in valid_transitions.get(current_status, []):
        conn.close()
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid transition: {current_status} -> {new_status}"
        )
        
    query = "UPDATE Incidents SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?"
    try:
        cursor.execute(query, (new_status, incident_id))
        
        # Log the transition
        cursor.execute('''
            INSERT INTO incident_audit_log (incident_id, old_status, new_status, actor)
            VALUES (?, ?, ?, ?)
        ''', (incident_id, current_status, new_status, 'System User')) # Hardcoded actor for now
        
        conn.commit()
        return {"success": True, "message": f"Status updated to {new_status}"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/incidents/{incident_id}", response_model=dict)
def delete_incident(incident_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Incidents WHERE id = ?", (incident_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")
        
    try:
        cursor.execute("DELETE FROM Incidents WHERE id = ?", (incident_id,))
        conn.commit()
        return {"success": True, "message": "Incident deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/incidents/{incident_id}/audit-log", response_model=List[dict])
def get_incident_audit_log(incident_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    query = "SELECT * FROM incident_audit_log WHERE incident_id = ? ORDER BY changed_at DESC"
    try:
        cursor.execute(query, (incident_id,))
        rows = cursor.fetchall()
        return [row_to_dict(cursor, row) for row in rows]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
