from fastapi import FastAPI, HTTPException, status, Query, Path, WebSocket, WebSocketDisconnect, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from schemas import IncidentCreate, IncidentUpdate, IncidentStatusUpdate
from database import get_db_connection
from datetime import datetime, timezone

app = FastAPI(title="Incident Tracker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Error Handlers ---
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_msg = ", ".join([f"{err['loc'][-1]}: {err['msg']}" for err in errors])
    return JSONResponse(
        status_code=422,
        content={"success": False, "error": error_msg},
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "error": exc.detail},
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal Server Error"},
    )

# --- WebSockets ---
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                pass

manager = ConnectionManager()

@app.websocket("/ws/incidents")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

def row_to_dict(cursor, row):
    if not row:
        return None
    return dict(row)

def get_utc_now():
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

# --- Routes ---
@app.post("/incidents", status_code=status.HTTP_201_CREATED)
async def create_incident(incident: IncidentCreate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    now = get_utc_now()
    query = """
    INSERT INTO Incidents (title, description, severity, status, reported_by, assigned_to, created_at, updated_at)
    VALUES (?, ?, ?, 'Open', ?, ?, ?, ?)
    RETURNING *
    """
    try:
        cursor.execute(query, (incident.title, incident.description, incident.severity, incident.reported_by, incident.assigned_to, now, now))
        row = cursor.fetchone()
        created_incident = row_to_dict(cursor, row)
        
        cursor.execute('''
            INSERT INTO incident_audit_log (incident_id, old_status, new_status, actor, changed_at)
            VALUES (?, NULL, 'Open', ?, ?)
        ''', (created_incident['id'], incident.reported_by, now))
        conn.commit()
        
        await manager.broadcast("update")
        return {"success": True, "data": created_incident}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/incidents")
def get_incidents(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    assigned_to: Optional[str] = None,
    sort_by: Optional[str] = Query("created_at", pattern="^(created_at|severity)$"),
    order: Optional[str] = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    base_query = "FROM Incidents WHERE 1=1"
    params = []
    
    if status:
        base_query += " AND status = ?"
        params.append(status)
    if severity:
        base_query += " AND severity = ?"
        params.append(severity)
    if assigned_to:
        base_query += " AND assigned_to = ?"
        params.append(assigned_to)
        
    cursor.execute(f"SELECT COUNT(*) {base_query}", params)
    total_records = cursor.fetchone()[0]

    order_dir = "ASC" if order.lower() == "asc" else "DESC"
    if sort_by == "severity":
        # Logical sort for severity
        order_col = """
            CASE severity 
                WHEN 'Critical' THEN 1 
                WHEN 'High' THEN 2 
                WHEN 'Medium' THEN 3 
                WHEN 'Low' THEN 4 
                ELSE 5 
            END
        """
    else:
        order_col = "created_at"
        
    query = f"SELECT * {base_query} ORDER BY {order_col} {order_dir} LIMIT ? OFFSET ?"
    
    params.append(page_size)
    params.append((page - 1) * page_size)
    
    try:
        cursor.execute(query, params)
        rows = cursor.fetchall()
        incidents = [row_to_dict(cursor, row) for row in rows]
        return {
            "success": True,
            "data": incidents,
            "total": total_records,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/incidents/analytics")
def get_analytics():
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT severity, COUNT(*) as count FROM Incidents GROUP BY severity")
        severity_counts = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT status, COUNT(*) as count FROM Incidents GROUP BY status")
        status_counts = [dict(row) for row in cursor.fetchall()]

        cursor.execute("SELECT date(created_at) as date, COUNT(*) as count FROM Incidents GROUP BY date(created_at) ORDER BY date(created_at) DESC LIMIT 7")
        daily_counts = [dict(row) for row in cursor.fetchall()]

        # Avg Resolution time (in hours) for closed incidents using audit log
        cursor.execute("""
            SELECT AVG((julianday(l.changed_at) - julianday(i.created_at)) * 24) as avg_hours
            FROM Incidents i
            JOIN incident_audit_log l ON i.id = l.incident_id
            WHERE i.status = 'Closed' AND l.new_status = 'Closed'
        """)
        avg_res = cursor.fetchone()
        avg_resolution_hours = round(avg_res[0], 2) if avg_res and avg_res[0] else 0

        return {
            "success": True,
            "data": {
                "severity_counts": severity_counts,
                "status_counts": status_counts,
                "daily_counts": daily_counts,
                "avg_resolution_hours": avg_resolution_hours
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/incidents/{incident_id}")
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
        return {"success": True, "data": row_to_dict(cursor, row)}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.put("/incidents/{incident_id}")
async def update_incident(incident_id: int, incident: IncidentUpdate):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM Incidents WHERE id = ?", (incident_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Incident not found")
        
    now = get_utc_now()
    query = """
    UPDATE Incidents 
    SET title = ?, description = ?, severity = ?, assigned_to = ?, updated_at = ?
    WHERE id = ?
    RETURNING *
    """
    try:
        cursor.execute(query, (incident.title, incident.description, incident.severity, incident.assigned_to, now, incident_id))
        row = cursor.fetchone()
        conn.commit()
        await manager.broadcast("update")
        return {"success": True, "data": row_to_dict(cursor, row)}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.patch("/incidents/{incident_id}/status")
async def update_status(incident_id: int, status_update: IncidentStatusUpdate):
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
        
    now = get_utc_now()
    query = "UPDATE Incidents SET status = ?, updated_at = ? WHERE id = ?"
    try:
        cursor.execute(query, (new_status, now, incident_id))
        
        cursor.execute('''
            INSERT INTO incident_audit_log (incident_id, old_status, new_status, actor, changed_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (incident_id, current_status, new_status, status_update.actor, now))
        
        conn.commit()
        await manager.broadcast("update")
        return {"success": True, "message": f"Status updated to {new_status}"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.delete("/incidents/{incident_id}")
async def delete_incident(incident_id: int):
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
        await manager.broadcast("update")
        return {"success": True, "message": "Incident deleted"}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

@app.get("/incidents/{incident_id}/audit-log")
def get_incident_audit_log(incident_id: int):
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection error")
    
    cursor = conn.cursor()
    query = "SELECT * FROM incident_audit_log WHERE incident_id = ? ORDER BY changed_at DESC"
    try:
        cursor.execute(query, (incident_id,))
        rows = cursor.fetchall()
        return {"success": True, "data": [row_to_dict(cursor, row) for row in rows]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
