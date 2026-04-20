# Zaptro Full-Stack Architecture Documentation

This document explains the comprehensive full-stack architecture implemented for the Zaptro Web Application, detailing the structure, the frontend/backend divide, files created, and APIs powered by FastAPI.

---

## 1. System Overview

The application was transformed from a purely static or third-party-dependent React frontend into a robust full-stack architecture.
- **Frontend Layer**: React (Vite) utilizing Context API for strict state management.
- **Backend Layer**: A high-performance Python **FastAPI** server that acts as the core controller.
- **Database Layer**: A local **SQLite** database managed natively through Python **SQLAlchemy** ORM.

### The Role of the Backend
Instead of your React app talking directly to external, public APIs (which can have CORS or availability issues—like FakeStore API breaking), all requests are routed through your FastAPI Backend. 

The backend handles:
1. **User Authentication** (Traditional Email/Password + Google Login)
2. **Product Caching & Proxying** (Translating dummyjson products to the format your frontend expects)
3. **Database Transactions** (Storing users safely into an SQLite file)

---

## 2. Backend Files Explained (`/backend` directory)

All core logic serverside lives in the `backend/` folder.

- **`main.py`**: The heart of the application. It initializes the FastAPI server, configures CORS (to allow your React app to communicate with it), and registers all the API endpoints `/login`, `/register`, `/products`, etc.
- **`database.py`**: Handles configuring the SQLite database (`sql_app.db`). It establishes the connection string and exposes a `get_db()` system that ensures database connections open and close safely per-request.
- **`models.py`**: Defines the physical database tables using SQLAlchemy. We created a `User` class here which translates to a `users` table with columns like `id`, `name`, `email`, and `hashed_password`.
- **`schemas.py`**: Uses Pydantic to strictly validate the data coming *into* and going *out* of our API. For example, if someone tries to register, Pydantic ensures they send a valid `email` and standard `password` payload.
- **`auth.py`**: The security hub. It handles hashing raw passwords using `bcrypt`, issuing secure JSON Web Tokens (JWT) for authenticated users, and verifying signatures on tokens generated natively by Google for the "Sign in with Google" flow.
- **`requirements.txt`**: The pip package manifest listing our core Python dependencies (fastapi, passlib, sqlalchemy, etc).

---

## 3. Frontend Files Explained (`/Frontend/src`)

- **`context/AuthContext.jsx`**: A global state store for the React app that persists user sessions. It verifies tokens via `jwt-decode`, binds the token specifically into the global `axios` header so all future API calls are inherently authenticated, and manages global login/out actions.
- **`pages/Login.jsx` & `pages/Register.jsx`**: The core authentication UI. Provides standard HTML input forms mixed with the `@react-oauth/google` buttons. Calls `POST /login` and `POST /google-login`.
- **`components/ProtectedRoute.jsx`**: A security boundary layer. If a user tries navigating to a secure route (like `/cart`) and the `AuthContext` sees they lack a valid token, it violently redirects them away to the `/login` page.
- **`App.jsx` & `main.jsx`**: Configured your React router architecture to wrap the foundational components inside the new `AuthProvider` and `GoogleOAuthProvider`.

---

## 4. Final API Endpoints Diagram

### Users & Security
- `POST http://localhost:8000/register`: Accepts `{email, password, name}`. Hashes password, saves to DB, returns user object.
- `POST http://localhost:8000/login`: Accepts `{email, password}`. Returns `{access_token: "jwt..."}`.
- `POST http://localhost:8000/google-login`: Accepts a Google ID Credential. Signs them into the database implicitly, returning your own local JWT access token.
- `GET http://localhost:8000/me`: A secure endpoint requiring a JWT token via headers to return user details.

### Product Proxying
Since the original external catalog crashed, these APIs were created to proxy `dummyjson.com` products reliably:
- `GET http://localhost:8000/products`: Returns the entire catalog. Uses in-memory Python caching so repeated load speeds drop to zero.
- `GET http://localhost:8000/products/{id}`: Returns details of a specific single product.
- `GET http://localhost:8000/products/category/{category}`: Fetches items exclusively for a specified subset (like electronics).

---

## 5. The SQLite Database Architecture

The SQLite engine automatically created a physical database file named `sql_app.db` locally in the `backend` folder.

**Table `users`:**
| Column Name        | Type    | Notes                                  |
|--------------------|---------|----------------------------------------|
| `id`               | Integer | Primary Key, Auto-incremented          |
| `name`             | String  | The user's name                        |
| `email`            | String  | Indexed, Unique email                  |
| `hashed_password`  | String  | Nullable (Null if User used Google)    |
