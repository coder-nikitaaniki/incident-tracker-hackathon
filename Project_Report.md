# Project Report: Incident Tracker

**Candidate Name:** Nikita
**Role:** Full-Stack Developer
**Duration:** 6 hours Hackathon

---

## 1. Project Overview
The Incident Tracker is a lightweight, responsive system designed to log, track, and triage production incidents. The application provides a seamless UI for users to report issues and a robust backend that enforces strict incident lifecycle transitions.

---

## 2. Requirements Checklist

### ✅ Phase 1: Core API & Database (100% Completed)
- **Data Model:** Designed relational database schema with correct types, `CHECK` constraints, `CREATE INDEX` statements for performance, and `ON DELETE CASCADE` for referential integrity.
- **CRUD API:** Developed full RESTful API (POST, GET, PUT, DELETE, PATCH).
- **Status Transitions:** Enforced strict lifecycle (`Open` -> `Investigating` -> `Resolved` -> `Closed`). Returns `400 Bad Request` for invalid moves.
- **Filtering & Sorting:** API supports filtering by status, severity, and assignment. Sorting dynamically handles severity correctly (Critical > High > Medium > Low).
- **Validation:** Implemented strict input validation (e.g., maximum 200 characters, whitespace trimming). Custom Exception Handlers enforce the required `{"success": false, "error": "..."}` JSON format across 422 and 500 errors.

### ✅ Phase 2: React.js Frontend (100% Completed)
- **Dashboard:** Created a clean table view using Material UI (MUI). Supports sorting and filtering controls dynamically fetching from the API.
- **Forms:** Added forms to Report new incidents and Edit existing ones (including `assigned_to`).
- **Detail View:** Dedicated view displaying incident info, severity, timeline history, and conditional status action buttons.

### 🚀 Phase 3: Stretch Goals (100% Completed for Bonus Credit)
- ✅ **3.1 Analytics Endpoint:** Added an `/incidents/analytics` API aggregating incidents. Accurately calculates average resolution time using Audit Log timestamps (unaffected by subsequent edits). Displayed using a new "Analytics" page with `recharts`.
- ✅ **3.2 Audit Log:** Added an `incident_audit_log` table to record every status change. Integrated into the Detail View to show a clear history timeline.
- ✅ **3.3 Pagination:** Added `page` and `page_size` (with an upper limit of 100) params to the list endpoint. The frontend dashboard utilizes an MUI `<Pagination>` control.
- ✅ **3.4 Tests:** Wrote a comprehensive `test_main.py` suite using `pytest`. The tests run on an isolated SQLite database (`test_incident_tracker.db`) that cleans up automatically. It thoroughly covers Create, Read (single, list, filters, sort, pagination), Update (PUT), Delete (with Cascade verification), and strict valid/invalid status-transition checks including 400, 404, and 422 custom HTTP errors.
- ✅ **3.5 Real-time Updates:** Integrated FastAPI WebSockets on `/ws/incidents`. The frontend connects to this websocket and automatically fetches the latest incidents instantly upon any creation or status update without requiring a manual refresh.

---

## 3. Architecture & Tech Stack
- **Frontend:** React.js, Vite, Material UI (MUI), Axios, React Router.
- **Backend:** FastAPI (Python 3.11+), Pydantic v2 (Data validation).
- **Database:** SQLite. 
  *(Note: As per the email update stating "You are free to choose any SQL database", SQLite was chosen over SQL Server to ensure zero-configuration, seamless local testing, and rapid development, while maintaining standard SQL relational architecture).*

---

## 4. Key Architecture Decisions & Trade-offs
1. **Error Formatting:** Overrode FastAPI's default `RequestValidationError` to strictly map 422 responses into the required `{success: false, error: ...}` format for strict contract adherence.
2. **Raw SQL vs ORM:** Raw SQL queries were used via Python's `sqlite3` driver. In a production scenario, an ORM like **SQLAlchemy** coupled with **Alembic** for migrations would be preferable for long-term maintainability.
3. **Database Constraints & Optimization:** Added performance indexes (`CREATE INDEX`) to filterable columns (status, severity, assigned_to). Enabled `PRAGMA foreign_keys=ON` so deleting an incident automatically cleans up its audit logs.
4. **Authentication (Trade-off):** Currently, there is no auth. "Current User" is hardcoded on the UI for status updates. Adding JWT authentication would be the next step to accurately track the `actor` and enforce role-based access control.
5. **Environment Configuration (Trade-off):** `http://localhost:8000` is hardcoded in the Axios calls. While standard practice dictates using `.env` variables (`VITE_API_URL`), this was omitted to simplify immediate out-of-the-box local hackathon testing.
