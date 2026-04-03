# Finance Dashboard Backend

A role-based finance management API built with **FastAPI**, **MongoDB**, and **JWT authentication**.

---

## Tech Stack

| Layer         | Technology                     |
|---------------|-------------------------------|
| Framework     | FastAPI 0.111                 |
| Database      | MongoDB (via Motor — async)   |
| Auth          | JWT (python-jose) + bcrypt    |
| Validation    | Pydantic v2                   |
| Runtime       | Python 3.11+                  |

---

## Project Structure

```
finance-backend/
├── main.py                        # App entry point, router registration
├── seed.py                        # DB seeder (sample users + transactions)
├── requirements.txt
├── .env.example
└── app/
    ├── core/
    │   ├── config.py              # Settings loaded from .env
    │   ├── database.py            # Async MongoDB client (Motor)
    │   └── security.py            # JWT creation/decoding, password hashing
    ├── models/
    │   └── enums.py               # UserRole, TransactionType, Category enums
    ├── schemas/
    │   ├── user.py                # User request/response Pydantic models
    │   ├── transaction.py         # Transaction models + filter + pagination
    │   └── dashboard.py           # Dashboard summary response models
    ├── middleware/
    │   └── auth.py                # JWT extraction + role-based dependencies
    ├── services/
    │   ├── user_service.py        # User CRUD business logic
    │   ├── transaction_service.py # Transaction CRUD + filter logic
    │   └── dashboard_service.py   # MongoDB aggregation pipelines
    └── routers/
        ├── auth.py                # POST /auth/register, /auth/login
        ├── users.py               # /users/* (admin-only management)
        ├── transactions.py        # /transactions/* (role-gated)
        └── dashboard.py           # GET /dashboard/summary
```

---

## Setup & Running

### Prerequisites
- Python 3.11+
- MongoDB running locally on port `27017` (or update `MONGODB_URL` in `.env`)

### 1. Clone and install dependencies

```bash
git clone <repo-url>
cd finance-backend
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set a strong SECRET_KEY
```

### 3. Seed the database (optional but recommended)

Creates 3 users and 15 sample transactions:

```bash
python seed.py
```

Seeded credentials:

| Role     | Email                   | Password     |
|----------|-------------------------|--------------|
| Admin    | admin@finance.dev       | admin123     |
| Analyst  | analyst@finance.dev     | analyst123   |
| Viewer   | viewer@finance.dev      | viewer123    |

### 4. Start the server

```bash
uvicorn main:app --reload
```

API is available at: `http://localhost:8000`  
Interactive docs: `http://localhost:8000/docs`

---

## Role Permissions

| Action                         | Viewer | Analyst | Admin |
|--------------------------------|--------|---------|-------|
| Register / Login               | ✅     | ✅      | ✅    |
| View own profile               | ✅     | ✅      | ✅    |
| List / view transactions       | ✅     | ✅      | ✅    |
| View dashboard summary         | ❌     | ✅      | ✅    |
| Create / update / delete tx    | ❌     | ❌      | ✅    |
| Manage users (CRUD)            | ❌     | ❌      | ✅    |

---

## API Reference

### Authentication

#### `POST /auth/register`
Register a new user (default role: viewer).

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "secret123"
}
```

#### `POST /auth/login`
Returns a JWT bearer token.

```json
{
  "email": "admin@finance.dev",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": { "id": "...", "name": "...", "role": "admin", ... }
}
```

---

### Users _(Admin only)_

| Method   | Path            | Description              |
|----------|-----------------|--------------------------|
| `GET`    | `/users/me`     | Get current user profile |
| `GET`    | `/users/`       | List all users           |
| `GET`    | `/users/{id}`   | Get user by ID           |
| `POST`   | `/users/`       | Create user with any role|
| `PATCH`  | `/users/{id}`   | Update user              |
| `DELETE` | `/users/{id}`   | Delete user              |

**Update user example:**
```json
{
  "role": "analyst",
  "status": "inactive"
}
```

---

### Transactions

| Method   | Path                    | Role          | Description           |
|----------|-------------------------|---------------|-----------------------|
| `GET`    | `/transactions/`        | All           | List with filters     |
| `GET`    | `/transactions/{id}`    | All           | Get one transaction   |
| `POST`   | `/transactions/`        | Admin         | Create transaction    |
| `PATCH`  | `/transactions/{id}`    | Admin         | Update transaction    |
| `DELETE` | `/transactions/{id}`    | Admin         | Delete transaction    |

**Create transaction body:**
```json
{
  "amount": 50000,
  "type": "income",
  "category": "salary",
  "date": "2024-05-01",
  "notes": "May salary"
}
```

**Supported filter query params:**

| Param        | Type   | Example              |
|--------------|--------|----------------------|
| `type`       | string | `income` / `expense` |
| `category`   | string | `salary`, `rent`, …  |
| `date_from`  | date   | `2024-01-01`         |
| `date_to`    | date   | `2024-06-30`         |
| `min_amount` | float  | `1000`               |
| `max_amount` | float  | `50000`              |
| `page`       | int    | `1`                  |
| `page_size`  | int    | `20` (max 100)       |

**Valid categories:** `salary`, `freelance`, `investment`, `food`, `transport`, `utilities`, `entertainment`, `healthcare`, `education`, `rent`, `other`

---

### Dashboard _(Analyst & Admin)_

#### `GET /dashboard/summary`

Returns aggregated analytics:

```json
{
  "total_income": 182000.00,
  "total_expense": 60400.00,
  "net_balance": 121600.00,
  "total_transactions": 15,
  "income_by_category": [
    { "category": "salary", "total": 175000, "count": 2 }
  ],
  "expense_by_category": [
    { "category": "rent", "total": 44000, "count": 2 }
  ],
  "monthly_trends": [
    { "year": 2024, "month": 5, "income": 90000, "expense": 30000, "net": 60000 }
  ],
  "recent_transactions": [ ... ]
}
```

---

## Error Responses

All errors follow a consistent format:

```json
{ "detail": "Human-readable error message" }
```

| Status | Meaning                              |
|--------|--------------------------------------|
| 400    | Validation error / bad input         |
| 401    | Missing or invalid token             |
| 403    | Insufficient role permissions        |
| 404    | Resource not found                   |
| 409    | Conflict (e.g. duplicate email)      |
| 422    | Pydantic validation failure          |
| 500    | Unexpected server error              |

---

## Assumptions & Design Decisions

1. **JWT-based auth over sessions** — stateless, suitable for a dashboard API consumed by a separate frontend.

2. **Viewer role reads transactions but not the dashboard** — the dashboard summary involves aggregation that's more analytical in nature, so it requires at least Analyst access. Viewers can still browse raw records.

3. **Admin creates/modifies transactions** — financial data integrity is treated as admin-level responsibility. Analysts are read-only consumers of that data.

4. **Soft-delete not implemented** — hard deletes were chosen for simplicity. A `is_deleted` flag can be added if an audit trail is required.

5. **No multi-tenancy** — all users share the same pool of transactions. A per-user or per-organization scope can be added by filtering on `created_by_id`.

6. **Dates stored as UTC datetime in MongoDB** — converted to `date` objects at the schema layer for clean API responses.

7. **Password stored as bcrypt hash** — never returned in any response; excluded at the query level.

8. **`/auth/register` defaults to viewer role** — privilege escalation requires an admin to explicitly assign a higher role via `PATCH /users/{id}`.

---

## Running in Production

- Set a strong random `SECRET_KEY` (32+ chars)
- Use a managed MongoDB instance (Atlas, etc.)
- Run with `uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4`
- Put behind a reverse proxy (nginx) with HTTPS
- Restrict `allow_origins` in the CORS middleware to your frontend domain
