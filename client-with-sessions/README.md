# Sessions Frontend Client

This React application provides a complete **session-based authentication flow** (sign up, log in, check session, log out). It is designed to connect to your **Flask backend** that manages user state using **Flask sessions**.

The client uses Flask sessions and the API routes described below. Its medication and schedule forms match the backend schemas in this project.

---

## Getting Started

1. **Install dependencies**
   ```bash
   npm install
   ```

2. **Start the application**
   ```bash
   npm start
   ```

3. **Backend requirements**
   - Must use **Flask sessions** to store and manage authentication.
   - Expose routes that manage login, signup, logout, and session checking.
   - Should run on port 5555 to match proxy in package.json.
   - Return JSON responses for all routes.

---

## Auth Flow Overview

This app handles user authentication and session state using the following endpoints:

---

### POST `/login`

**Description**: Authenticates an existing user and sets the session cookie.  
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Body**:
```json
{
  "username": "string",
  "password": "string"
}
```

**Response**:
```json
{
  "id": 1,
  "username": "string"
}
```

---

### POST `/signup`

**Description**: Registers a new user and logs them in by setting the session.  
**Headers**:
```json
{
  "Content-Type": "application/json"
}
```

**Body**:
```json
{
  "username": "string",
  "password": "string",
  "password_confirmation": "string"
}
```

**Response**:
```json
{
  "id": 1,
  "username": "string"
}
```

---

### 🔄 GET `/check_session`

**Description**: Verifies if a user session is active.  
**Headers**: _(none required)_

**Response (if logged in)**:
```json
{
  "id": 1,
  "username": "string"
}
```

**Response (if not logged in)**:
```json
{"errors":["Authentication required"]}
```
Status: `401`

---

### DELETE `/logout`

**Description**: Ends the session by removing `user_id` from the session store.  
**Headers**: _(none required)_

**Response**: `204 No Content`

---

## Session Management

- When a user logs in or signs up, a session is created on the server.
- `check_session` is used on initial load to verify if a user is still logged in.
- On logout, the session is destroyed server-side and the frontend state is cleared.

---

## This Flask project

The client uses the Create React App proxy in `package.json` to send relative
requests to Flask on `http://localhost:5555`. Run the React app at
`http://localhost:4000`, which is the origin allowed by the Flask CORS setup.
Session requests include credentials.

Medication requests use the routes implemented in `routes/medication_routes.py`:

- `POST /api/medications/addmedication`
- `GET /api/medications/getmedications`
- `PATCH /api/medications/update/<id>`
- `DELETE /api/medications/delete/<id>`

The medication request fields are `name`, `dosage`, `instructions`,
`start_date`, and `end_date`.

Schedules use `/api/schedules`; doses and dose status updates use `/api/doses`.
Those blueprints exist in the backend source, but the `create_app()` used by
`run.py` currently registers only medications and reports. Register
`schedules_bp` and `dose_bp` in that app before using schedule management or
the Taken/Missed buttons. The daily dose report at `/api/reports/daily` is
registered and can be viewed without those blueprints.

---
