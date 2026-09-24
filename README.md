# Incident Tracker

A lightweight system to log, track, and triage production incidents. Built for the Hackathon Interview.

## Architecture

* **Frontend:** React.js, Vite, Material UI
* **Backend:** FastAPI, Python (Requires Python 3.11+)
* **Database:** SQLite (Chosen as per the email update allowing any SQL database)

## Setup Instructions

### 1. Database Setup
1. The application uses **SQLite** for zero-configuration testing.
2. The database file (`incident_tracker.db`) is generated automatically. It utilizes `PRAGMA foreign_keys = ON` and `ON DELETE CASCADE` to keep audit logs clean upon incident deletion.

### 2. Backend Setup
1. Navigate to the `backend` directory.
2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   
   # Mac/Linux
   python3 -m venv venv
   source venv/bin/activate
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
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite server:
   ```bash
   npm run dev
   ```
   The frontend will be running at `http://localhost:5173`.

### 4. Running Tests
The backend contains a comprehensive test suite that runs against an isolated, automatically-cleaned temporary SQLite database.
1. From the `backend` directory, run:
   ```bash
   pytest
   ```

## Features Implemented
* **Phase 1: Core API & Database:** Full CRUD (including PUT updates), Strict Status Transitions, Dynamic Filtering & Custom Severity Sorting, Input Validation (Custom 422 JSON format). Database features Table Indexes and Cascade Deletes.
* **Phase 2: React.js Frontend:** Dashboard list, Filters & Sort controls, Create/Edit Incident forms, Detail view, and Status Actions.
* **Phase 3: Stretch Goals (100% Completed)**
  * **3.1 Analytics Endpoint:** Data aggregation for severity, status, daily counts, and exact average resolution time using audit logs.
  * **3.2 Audit Log:** Complete timeline tracking of status changes and actors.
  * **3.3 Pagination:** Server-side pagination supported seamlessly on the UI.
  * **3.4 Tests:** Comprehensive `pytest` coverage for logic, filters, errors, and transitions.
  * **3.5 Real-time Updates:** FastAPI WebSockets immediately refresh the React UI upon any incident update.

## Trade-offs & Future Improvements
* **Database Choice:** SQLite was preferred for simplicity. In production, PostgreSQL with SQLAlchemy/Alembic would be ideal.
* **Authentication:** Currently there is no auth. "Current User" is hardcoded on the UI for status updates. Adding JWT would properly resolve user attribution.
* **Hardcoded Environments:** `http://localhost:8000` is hardcoded in the frontend for ease of running this hackathon locally. A production app would use `import.meta.env.VITE_API_URL`.
