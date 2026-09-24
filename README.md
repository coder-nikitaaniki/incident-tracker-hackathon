# Incident Tracker

A lightweight system to log, track, and triage production incidents. Built for the Hackathon Interview.

## Architecture

* **Frontend:** React.js, Vite, Material UI
* **Backend:** FastAPI, Python, `sqlite3`
* **Database:** SQLite (Chosen as per the email update allowing any SQL database)

## Setup Instructions

### 1. Database Setup
1. The application uses **SQLite** for simplicity and ease of setup.
2. You do not need to run any external SQL scripts. The database file (`incident_tracker.db`) and the required tables (`Incidents` and `incident_audit_log`) will be **automatically created** the first time you run the backend server.

### 2. Backend Setup
1. Navigate to the `backend` directory.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
   The API will be running at `http://localhost:8000`.

### 3. Frontend Setup
1. Navigate to the `frontend` directory.
2. Install dependencies (if not already done):
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173`.

## Features Implemented
* **Phase 1: Core API & Database** (Data Model, CRUD API, Status Transitions, Filtering & Sorting, Validation)
* **Phase 2: React.js Frontend** (Dashboard list, Filters, Create Incident form, Incident Detail view, Status Actions)
* **Phase 3: Stretch Goal - Audit Log** (Tracks and displays a timeline of all status changes for an incident)

## Trade-offs & Future Improvements
* **Database Choice:** Leveraged SQLite for zero-configuration local testing as permitted by the instructions. In a production environment, PostgreSQL or SQL Server with an ORM like SQLAlchemy and Alembic for migrations would be preferred.
* **State Management:** Used React local state and Axios for simplicity. In a larger app, React Query or Redux might be better for caching and global state management.
* **Authentication:** Currently there is no auth. We'd want to add JWT authentication and restrict status transitions based on user roles.
