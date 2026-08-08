# Location-Based Attendance Tracking System

A full-stack attendance tracker: employees check in/out using their device's
GPS, and their location is validated against an office geofence. Suspicious
check-ins (out of range, poor GPS, GPS spoofing, duplicate/rapid check-ins)
are flagged for admin review.

This build has **no login system**. Role is switched with a button in the UI,
which is the intended way to demo both the employee and admin experience —
see [How roles work](#how-roles-work) below.

## Tech stack

- **Backend:** FastAPI (Python), SQLAlchemy, PostgreSQL
- **Frontend:** React 19 + Vite, axios

## Quick Start (~2 min)

**Prerequisites:** Python 3.11+, Node 18+, a running PostgreSQL instance.

### 1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Edit `backend/.env` if your Postgres credentials differ from the defaults:

```
DATABASE_URL=postgresql://postgres:<password>@localhost:5432/attendance_db
DEBUG=True
```

Create the database, then seed it:

```bash
python init_db.py            # creates tables (drops existing ones first)
python create_test_data.py   # seeds 1 office + 2 employees
uvicorn app.main:app --reload
```

Backend runs at **http://localhost:8000** — interactive API docs at
**http://localhost:8000/docs**.

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at **http://localhost:5173**.

## How roles work

There's no login. The app ships with two seeded employees:

| ID | Name | Role |
|----|------|------|
| 1 | Employee User | Employee |
| 2 | Admin User | Admin |

The **"Switch to Admin / Switch to Employee"** button in the header flips
which employee ID the frontend acts as. Switching to Admin reveals the
**Admin** tab in the nav bar. This is a UI-level convenience for demoing both
roles from one browser tab — the API itself doesn't enforce who can call
which endpoint (see [Design note](#design-note-no-authentication) below).

## What each tab does

- **📍 Check-In** — Fetches your GPS location, shows distance from the
  office, and lets you check in / check out. Check-ins outside the geofence,
  with poor GPS accuracy, or flagged as suspicious are marked "pending
  approval" instead of failing outright.
- **📋 History** — Last 30 attendance records for the current role
  (employee 1 or 2), with status (valid / flagged).
- **👨‍💼 Admin** *(visible only in Admin role)* — Lists all flagged
  check-ins awaiting review, with Approve / Reject actions.

## Testing both roles

1. Open the app as **Employee** (default). Click **Get Location**, then
   **Check In**. If your machine's location resolves within ~100m of the
   seeded Mumbai office (19.0760, 72.8777), it succeeds immediately.
2. Click **Switch to Admin**. Check in as the admin employee too, from a
   location far from the office, to generate a flagged record.
3. Open the **Admin** tab and Approve or Reject the flagged check-in.
4. Switch back to **Employee** and check the **History** tab to see the
   updated status.

> Browser geolocation on `localhost` usually needs to be allowed when
> prompted. Most laptops resolve to a Wi-Fi-based location rather than GPS,
> so don't be surprised if you're "far" from the seeded office — that's
> expected, and it's a good way to trigger the flagged/admin-review flow.

## Features

- GPS geofence validation (Office mode) with a configurable radius
- Field mode for check-ins from anywhere
- Fraud detection: poor GPS accuracy, mock/spoofed location, impossible
  travel speed between check-ins, duplicate check-ins within 5 minutes
- Admin review queue for flagged check-ins (approve/reject)
- Attendance history per employee

## Troubleshooting

- **"Failed to load office location" on the Check-In screen** — the backend
  isn't running, or the DB hasn't been seeded. Run `create_test_data.py`.
- **CORS errors in the browser console** — make sure the frontend is running
  on `localhost:5173` (or `3000`/`5174`); the backend's CORS list is
  hardcoded to those origins in `app/main.py`.
- **Database connection errors** — check `DATABASE_URL` in `backend/.env`
  matches your local Postgres user/password/port, and that the
  `attendance_db` database exists.
- **Geolocation prompt never appears / times out** — browser location
  permissions may be blocked; check your browser's site settings for
  `localhost`.

## File structure

```
backend/
  app/
    main.py               # FastAPI app, CORS, router registration
    database.py            # SQLAlchemy engine/session setup
    models.py               # Employee, OfficeLocation, AttendanceRecord, SuspiciousCheckIn
    routes/
      attendance.py         # check-in / check-out / history / office-locations
      admin.py               # suspicious check-in review (approve/reject)
    services/
      distance.py            # haversine distance calculation
      fraud_detection.py     # GPS accuracy / speed / duplicate checks
      audit_logger.py        # console audit logging
  create_test_data.py       # seeds 1 office + 2 employees
  init_db.py                 # (re)creates all tables
  requirements.txt
  .env                        # DATABASE_URL, DEBUG

frontend/
  src/
    App.jsx                  # nav + role toggle
    components/
      CheckInScreen.jsx       # GPS check-in/out UI
      HistoryScreen.jsx        # attendance history
      AdminPanel.jsx            # flagged check-in review
    services/
      api.js                    # axios client (attendance + admin endpoints)
      locationService.js         # browser geolocation + distance helper
```

## Design note: no authentication

This project intentionally ships without a login/auth system — role is a
UI-only toggle between two seeded employee IDs, and no endpoint checks who's
calling it. That's fine for a local demo, but **don't deploy this to a
public network as-is**: anyone with API access can act as any employee,
including the admin-only approve/reject actions. Adding real authentication
(e.g. JWT + password hashing) would be a natural next step before any real
deployment.

## Future Work & Production Roadmap

### Phase 1: Security Hardening
- [ ] Add velocity-based fraud detection (prevent impossible travel across cities)
- [ ] Input validation on all endpoints (validate GPS coordinates, accuracy ranges)
- [ ] Replace binary `is_valid` with confidence scoring (0.0-1.0 scale)
- [ ] Add audit logging to track admin approvals/rejections with timestamps
- [ ] Implement replay attack protection with cryptographic signatures

### Phase 2: Enhanced Fraud Detection
- [ ] IP geolocation verification (flag if GPS and IP locations differ >50km)
- [ ] Biometric verification on mobile (fingerprint/face ID for sensitive roles)
- [ ] Device binding detection (prevent rapid device switching)
- [ ] Behavioral anomaly detection (unusual check-in patterns)
- [ ] Enhanced device fingerprinting (MAC address, IMEI, Android ID)

### Phase 3: Operational Readiness
- [ ] Real password-based authentication (replace demo role toggle)
- [ ] Multi-polygon geofencing (handle multi-building offices)
- [ ] Offline sync strategy for mobile workers
- [ ] WiFi/cellular fallback when GPS unavailable
- [ ] Admin dashboard with analytics and reporting
- [ ] Data retention policy & GDPR compliance

### Phase 4: Scalability & Deployment
- [ ] Database indexing optimization
- [ ] Redis caching for office locations
- [ ] Rate limiting on auth endpoints
- [ ] Webhook notifications for flagged check-ins
- [ ] Mobile app hardening (certificate pinning, jailbreak detection)

## Known Limitations

- Mock location detection flags spoofing but doesn't cross-validate with other signals
- Device fingerprinting limited to device_id only (future: MAC address, IMEI)
- Single circular geofence per office (future: polygon-based for complex buildings)
- No velocity analysis between check-ins (future: implement in Phase 1)
- Admin decisions not audit-logged (future: add admin_id + timestamp tracking)