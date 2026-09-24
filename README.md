# Incident Tracker

A lightweight system to log, track, and triage production incidents. Built for the Hackathon Interview.

## Architecture

* **Frontend:** React.js, Vite, Material UI
* **Backend:** FastAPI, Python, PyODBC
* **Database:** SQL Server

## Setup Instructions

### 1. Database Setup
1. You need a running SQL Server instance.
2. Run the `db/schema.sql` script on your SQL Server to create the `IncidentTracker` database and the `Incidents` table.
3. Update the `backend/.env` file with your SQL Server connection details.

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

## Trade-offs & Future Improvements
* **Database Driver:** Used raw `pyodbc` as requested, but in a production environment, an ORM like SQLAlchemy with Alembic for migrations would be preferred for maintainability.
* **State Management:** Used React local state and Axios for simplicity. In a larger app, React Query or Redux might be better for caching and global state.
* **Authentication:** Currently there is no auth. We'd want to add JWT authentication and user roles.
