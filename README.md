# 🔥 LinkFlare — URL Shortener with Analytics

> A URL shortener to Shorten any URL, track every click with country, referrer, and user agent data, and visualize it all on a per-link analytics dashboard.

**Live:** [https://linkflare.lalonhobekotodine.sbs](https://linkflare.lalonhobekotodine.sbs)

**API Docs:** [https://linkflare.lalonhobekotodine.sbs/docs](https://linkflare.lalonhobekotodine.sbs/docs)

---

## Screenshots

> Dashboard · Analytics · API Docs

---

## What It Does

- Shorten any URL and get a short code (e.g. `linkflare.lalonhobekotodine.sbs/Fs9XpJ`)
- Every redirect is tracked: timestamp, country (via IP geolocation), referrer, user agent
- Per-link analytics dashboard with click breakdown by country
- JWT authentication — register, login, manage your own links
- Custom short codes support (`/my-brand`)
- Link expiry with automatic background cleanup
- Redis-based rate limiting on redirects and link creation
- Clean single-page dashboard UI — no frameworks, pure HTML/CSS/JS

---

## Tech Stack

| Layer | Technology |
|---|---|
| **API** | FastAPI + Uvicorn |
| **Database** | SQLite (via aiosqlite) + SQLAlchemy 2.0 async ORM |
| **Migrations** | Alembic |
| **Auth** | JWT (python-jose) + bcrypt password hashing (passlib) |
| **Rate Limiting** | Redis |
| **Background Jobs** | APScheduler — hourly cleanup of expired links |
| **Geolocation** | ip-api.com (free, no API key needed) |
| **Frontend** | Jinja2 templates + vanilla JS + Chart.js |
| **Containerization** | Docker multi-stage build, non-root user |
| **CI/CD** | GitHub Actions → GHCR → VPS SSH deploy |
| **Reverse Proxy** | Nginx + Let's Encrypt TLS (Certbot) |

---

## Architecture

```
Browser / Client
      │
      ▼
  Nginx (TLS, port 443)
      │
      ▼
  Docker Container
  ┌─────────────────────────┐
  │  FastAPI + Uvicorn      │
  │  ┌──────────────────┐   │
  │  │  SQLite DB       │   │
  │  │  (persistent     │   │
  │  │   volume mount)  │   │
  │  └──────────────────┘   │
  │  ┌──────────────────┐   │
  │  │  Redis           │   │
  │  │  (rate limiting) │   │
  │  └──────────────────┘   │
  └─────────────────────────┘
```

**CI/CD Pipeline:**
```
git push main
    │
    ├── pytest (11 tests)
    │
    ├── Docker multi-stage build → push to GHCR
    │
    └── SSH into VPS → docker compose pull → up -d
```

---

## API Endpoints

| Method | Path | Auth | Description |
|---|---|---|---|
| `POST` | `/auth/register` | — | Create account |
| `POST` | `/auth/login` | — | Get JWT token |
| `POST` | `/links/` | ✓ | Create short link |
| `GET` | `/links/` | ✓ | List your links |
| `DELETE` | `/links/{code}` | ✓ | Delete a link |
| `GET` | `/{code}` | — | Redirect + track click |
| `GET` | `/analytics/{code}` | ✓ | Analytics dashboard (HTML) |
| `GET` | `/analytics/{code}/json` | ✓ | Analytics data (JSON) |
| `GET` | `/health` | — | Health check |
| `GET` | `/` | — | Web dashboard |

---

## Project Structure

```
linkflare/
├── app/
│   ├── main.py              # FastAPI app factory + lifespan
│   ├── config.py            # Settings via pydantic-settings
│   ├── database.py          # Async SQLAlchemy engine + session
│   ├── models.py            # ORM models: User, Link, Click
│   ├── schemas.py           # Pydantic request/response schemas
│   ├── dependencies.py      # JWT auth, Redis client, rate limiter
│   ├── routers/
│   │   ├── auth.py          # Register + login
│   │   ├── links.py         # Link CRUD
│   │   ├── redirect.py      # Redirect + click tracking
│   │   └── analytics.py     # Analytics endpoints
│   ├── services/
│   │   ├── shortener.py     # Collision-safe code generation
│   │   ├── geolocation.py   # IP → country via ip-api.com
│   │   └── cleanup.py       # APScheduler expired link cleanup
│   └── templates/
│       ├── index.html       # Single-page dashboard UI
│       └── dashboard.html   # Server-side analytics view
├── alembic/                 # Database migrations
├── tests/
│   ├── conftest.py          # Async test client + DB overrides
│   ├── test_auth.py
│   ├── test_links.py
│   └── test_redirect.py
├── .github/workflows/
│   └── deploy.yml           # CI/CD pipeline
├── Dockerfile               # Multi-stage, non-root appuser
├── docker-compose.yml       # Local dev: app + redis
└── docker-compose.prod.yml  # Production overrides
```

---

## Local Development

**Prerequisites:** Python 3.12+, Redis running locally

```bash
# 1. Clone and enter
git clone https://github.com/avsk-net/linkflare.git
cd linkflare

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set SECRET_KEY to output of: openssl rand -hex 32

# 4. Run migrations
alembic upgrade head

# 5. Start the app
uvicorn app.main:app --reload

# Visit http://localhost:8000
# API docs at http://localhost:8000/docs
```

---

## Running with Docker

```bash
cp .env.example .env
# fill in SECRET_KEY in .env

docker compose up -d

# Visit http://localhost:8000
```

This starts:
- `app` — FastAPI on port 8000
- `redis` — Redis on port 6379

---

## Running Tests

```bash
pytest tests/ -v
```

```
tests/test_auth.py::test_register              PASSED
tests/test_auth.py::test_duplicate_register    PASSED
tests/test_auth.py::test_login                 PASSED
tests/test_auth.py::test_wrong_password        PASSED
tests/test_links.py::test_create_link          PASSED
tests/test_links.py::test_list_links           PASSED
tests/test_links.py::test_custom_code          PASSED
tests/test_links.py::test_delete_link          PASSED
tests/test_redirect.py::test_redirect          PASSED
tests/test_redirect.py::test_redirect_not_found PASSED
tests/test_redirect.py::test_click_count_increments PASSED

11 passed
```

Tests use an in-memory SQLite database and disable Redis rate limiting automatically via dependency overrides.

---

## Environment Variables

| Variable | Description | Example |
|---|---|---|
| `DATABASE_URL` | SQLAlchemy async DB URL | `sqlite+aiosqlite:///./linkflare.db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `SECRET_KEY` | JWT signing key (keep secret) | `openssl rand -hex 32` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `60` |
| `BASE_URL` | Public base URL for short links | `https://linkflare.yourdomain.com` |
| `ENVIRONMENT` | `development` or `production` | `production` |

---

## Deployment

This project deploys automatically on every push to `main` via GitHub Actions:

1. **Test** — runs pytest against SQLite in-memory DB
2. **Build & Push** — Docker multi-stage build pushed to GHCR
3. **Deploy** — SSH into VPS, pull new image, `docker compose up -d`

**Required GitHub Secrets:**

| Secret | Description |
|---|---|
| `VPS_HOST` | VPS IP address |
| `VPS_SSH_KEY` | Private SSH key for deploy user |
| `GHCR_TOKEN` | GitHub PAT with `read:packages` |

**VPS requirements:** Ubuntu, Docker, Nginx, Certbot

---

## What I Learned Building This

Compared to [Project 1 — InfraPulse](https://github.com/avsk-net/infra-pulse), this project added:

- **Async SQLAlchemy 2.0** with proper session management and relationship loading
- **Alembic migrations** — schema versioning for production databases
- **JWT auth flow** — token creation, validation, dependency injection pattern
- **Redis rate limiting** — sliding window counter per IP/user
- **Background scheduling** — APScheduler wired into FastAPI lifespan
- **IP geolocation** — async HTTP calls to external API with graceful fallback
- **Debugging Docker networking** — port binding conflicts, iptables chain issues, container user permissions
- **Production Nginx config** — TLS termination, proxy headers for real IP forwarding

---

## Portfolio Series

| Project | Description | Status |
|---|---|---|
| [InfraPulse](https://github.com/avsk-net/infra-pulse) | Infrastructure health-check API | ✅ Live |
| **LinkFlare** | URL shortener with analytics | ✅ Live |
| Project 2 | *(coming soon)* | 🚧 |

---

[GitHub](https://github.com/avsk-net)
