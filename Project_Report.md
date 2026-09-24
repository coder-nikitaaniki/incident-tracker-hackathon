# Project Report: Incident Tracker

**Candidate Name:** Nikita
**Role:** Full-Stack Developer
**Duration:** 6 hours Hackathon

---

## 1. Project Overview
The Incident Tracker is a lightweight, responsive system designed to log, track, and triage production incidents. The application provides a seamless UI for users to report issues and a robust backend that enforces strict incident lifecycle transitions.

---

## 2. Requirements Checklist (What is Done vs. What is Not Done)

### ✅ Phase 1: Core API & Database (100% Completed)
- **Data Model:** Designed relational database schema with correct types and constraints.
- **CRUD API:** Developed full RESTful API using FastAPI for Create, Read, Update, and Delete operations.
- **Status Transitions:** Enforced strict lifecycle (`Open` -> `Investigating` -> `Resolved` -> `Closed`). Returns `400 Bad Request` for invalid moves.
- **Filtering & Sorting:** API supports filtering by status and severity, and sorts results by creation date.
- **Validation:** Implemented strict input validation (e.g., maximum 200 characters for title, restricted severity values). Returns clear `422` error messages.

### ✅ Phase 2: React.js Frontend (100% Completed)
- **Dashboard:** Created a clean table/list view using Material UI (MUI).
- **Create Form:** Added a modal dialog to report new incidents easily.
- **Detail View:** Implemented a dedicated view for individual incidents to see full descriptions and history.
- **Filters:** Built UI controls for Status and Severity that trigger server-side filtering via API query params.
- **Status Actions:** Built dynamic buttons that only allow valid status transitions (e.g., hiding the 'Investigating' button if the incident is already 'Resolved').

### 🚀 Phase 3: Stretch Goals (Partially Completed for Bonus Credit)
- ❌ 3.1 Analytics Endpoint: Not implemented (prioritized core stability and Audit Log).
- ✅ **3.2 Audit Log: COMPLETED.** Added an `incident_audit_log` table to record every status change with a timestamp and actor. Integrated into the Detail View to show a clear history timeline.
- ❌ 3.3 Pagination: Not implemented.
- ❌ 3.4 Tests: Not implemented.
- ❌ 3.5 Real-time Updates: Not implemented.

---

## 3. Architecture & Tech Stack
- **Frontend:** React.js, Vite, Material UI (MUI), Axios, React Router.
- **Backend:** FastAPI (Python), Pydantic (Data validation).
- **Database:** SQLite. 
  *(Note: As per the email update stating "You are free to choose any SQL database", SQLite was chosen over SQL Server to ensure zero-configuration, seamless local testing, and rapid development, while maintaining standard SQL relational architecture).*

---

## 4. Database Schema Details
1. **`Incidents` Table:**
   - Primary data store for incidents.
   - Utilizes `CHECK` constraints to ensure `status` and `severity` strictly adhere to the allowed enums at the database level.
2. **`incident_audit_log` Table:**
   - Tracks the history of status transitions.
   - Uses a `FOREIGN KEY (incident_id)` referencing the `Incidents` table.

---

## 5. Key Architecture Decisions & Trade-offs
1. **Backend Validation vs Frontend Validation:**
   - While the React frontend hides invalid status buttons, the core validation logic is heavily enforced on the backend. This ensures the API remains secure even if invoked via Postman or third-party clients.
2. **Raw SQL vs ORM:**
   - Raw SQL queries were used via Python's `sqlite3` driver to demonstrate proficiency in writing raw queries and to keep the setup lightweight. In a production scenario, an ORM like **SQLAlchemy** coupled with **Alembic** for migrations would be preferable for long-term maintainability.
3. **State Management:**
   - React's local state (`useState`, `useEffect`) was sufficient for this application's scope. For a larger-scale enterprise app, global state management like **Redux** or **React Query** (for data caching) would be implemented.
4. **Authentication:**
   - Currently, user names are inputted manually as strings. With more time, a proper **JWT-based Authentication** system would be added to accurately track the `actor` in the Audit Log and enforce role-based access control.
