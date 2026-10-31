# Sessions Frontend Client

This React application provides a complete **session-based authentication flow** (sign up, log in, check session, log out). It is designed to connect to your **Flask backend** that manages user state using **Flask sessions**.

You will not need to modify this frontend. However, your backend must implement and support the routes described below for the client to function properly.

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
{}
```

---

### DELETE `/logout`

**Description**: Ends the session by removing `user_id` from the session store.  
**Headers**: _(none required)_

**Response**:
```json
{}
```

---

## Session Management

- When a user logs in or signs up, a session is created on the server.
- `check_session` is used on initial load to verify if a user is still logged in.
- On logout, the session is destroyed server-side and the frontend state is cleared.

---

## Custom Resource Endpoints

This frontend does **not include fetch calls** for your custom resource (e.g., `/notes`, `/entries`, `/tasks`). These will be added by the frontend team after your backend is complete.

Ensure your resource routes:
- Are fully protected: require login to access.
- Use `session['user_id']` to associate and filter data per user.
- Follow RESTful patterns: `GET`, `POST`, `PATCH`, `DELETE`.
- Include pagination support where appropriate (e.g., `GET /notes?page=1&per_page=10`).

---
