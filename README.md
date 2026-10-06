# Sentinel AI

Sentinel AI is a security operations dashboard with a React frontend, a FastAPI backend, real-time event processing, and an endpoint agent. The frontend is built with Vite and connects to the existing Render API deployment.

## Project structure

| Path | Purpose |
| --- | --- |
| `frontend/` | React and Vite dashboard, including the Vercel build target |
| `backend/` | FastAPI application, authentication, APIs, and event processing |
| `endpoint_agent/` | Endpoint telemetry collection agent |
| `ai_engine/`, `ai_agent/`, `agent/` | Detection, analysis, response, and agent modules |
| `deployment/` | Windows endpoint installation scripts and Nginx configuration |
| `docker-compose*.yml`, `Dockerfile*` | Container-based deployment definitions |
| `.github/workflows/` | GitHub Actions workflow |

## Run locally

Requirements: Python 3.10 or newer and Node.js 24 LTS for local development.

### Backend

From the repository root, create and activate a virtual environment, install the backend requirements, and start the API:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
$env:SECRET_KEY = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:SENTINEL_AGENT_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:SENTINEL_INITIAL_ADMIN_PASSWORD = Read-Host "Choose a unique local admin password"
$env:SENTINEL_CORS_ORIGINS = "http://localhost:5173"
Set-Location backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`. For a local endpoint agent, provide the same `SENTINEL_AGENT_TOKEN` in its environment or the `agent_token` field of `C:\ProgramData\SentinelAI\config.json`.

### Frontend

In a second terminal from the repository root:

```powershell
Set-Location frontend
$env:VITE_API_URL = "http://127.0.0.1:8000"
npm ci
npm run dev
```

Vite prints the local dashboard URL when the development server starts.

## Existing hosted deployments

The frontend is the Vite application in `frontend/`, and the backend is deployed separately on Render. Keep the current Vercel project connected to this repository with its existing project settings. If configuring a new Vercel project, use `frontend` as the Root Directory, `npm run build` as the Build Command, and `dist` as the Output Directory.

The deployed frontend defaults to the existing Render API URL, `https://sentinel-ai-fz5u.onrender.com`; hosted builds do not use localhost. In Vercel, set `VITE_API_URL` to the full Render backend origin if your Render service has a different URL. Do not set it to `/api` on Vercel: that relative path is only for the Docker/Nginx profile, where Nginx proxies requests to the Compose backend. The WebSocket URL is derived from the configured API host unless `VITE_WS_URL` is set.

For the backend on Render, configure `SECRET_KEY` with a random value of at least 32 characters, `SENTINEL_AGENT_TOKEN` with a separate random value of at least 32 characters, and `SENTINEL_CORS_ORIGINS` with the exact Vercel site origin (for example, `https://your-app.vercel.app`; no path or trailing slash). The backend intentionally has no localhost CORS default: browser access works only after this hosted origin is configured. The dashboard and report downloads use an admin bearer token. The endpoint agent uses `SENTINEL_AGENT_TOKEN` for heartbeat, process, USB, and endpoint-session uploads. Set `SENTINEL_INITIAL_ADMIN_PASSWORD` only if the database does not yet contain the `admin` account; this setting creates that account on first startup and does not reset an existing password. The backend also accepts `INITIAL_ADMIN_PASSWORD` or `ADMIN_PASSWORD` as aliases. Never put secret values in Git or send them in chat.

Set the same `SENTINEL_AGENT_TOKEN` in the Render backend environment and install each Windows agent with that token. The installer prompts for it without echoing the value and stores it in an ACL-restricted file under `C:\ProgramData\SentinelAI`. Rotating the shared agent token requires updating Render and reinstalling or updating every agent configuration.

The dashboard logout endpoint revokes all outstanding admin tokens for that account immediately. It closes local real-time sockets at once; sockets on another application instance recheck the token version within 30 seconds. If the browser cannot reach the backend during logout, it clears the local session but reports that server revocation was not confirmed; any copied token remains usable until its normal expiry.

## Container deployment

For the Docker-based office/LAN deployment, see [deployment/README.md](deployment/README.md). That guide covers the production Compose profile and Windows endpoint agent installation.

## Configuration and security

- Copy `.env.example` to `.env` for backend settings and replace example secrets before deployment.
- Keep `.env` and provider API keys out of Git; use the deployment platform's environment-variable settings for hosted services.
- Do not use demo or default credentials in a production environment.
- Restrict CORS origins and enable HTTPS for production deployments.

## License

No license is currently specified. Contact the repository owner before reusing or distributing this project.
