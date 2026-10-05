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

Requirements: Python 3.10 or newer and Node.js 20 or newer.

### Backend

From the repository root, create and activate a virtual environment, install the backend requirements, and start the API:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
$env:SECRET_KEY = "set-a-random-secret-at-least-32-characters"
$env:SENTINEL_INITIAL_ADMIN_PASSWORD = "choose-a-unique-admin-password"
$env:SENTINEL_CORS_ORIGINS = "http://localhost:5173"
Set-Location backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`.

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

The frontend defaults to the existing Render API URL, `https://sentinel-ai-fz5u.onrender.com`. You can override it in Vercel with `VITE_API_URL`; the WebSocket URL is derived from the same host unless `VITE_WS_URL` is set.

For the backend on Render, configure `SECRET_KEY` with a random value of at least 32 characters and `SENTINEL_CORS_ORIGINS` with the exact Vercel site origin (for example, `https://your-app.vercel.app`). Set `SENTINEL_INITIAL_ADMIN_PASSWORD` only if the database does not yet contain the `admin` account; this setting creates that account on first startup and does not reset an existing password. The backend also accepts `INITIAL_ADMIN_PASSWORD` or `ADMIN_PASSWORD` as aliases. Never put secret values in Git or send them in chat.

## Container deployment

For the Docker-based office/LAN deployment, see [deployment/README.md](deployment/README.md). That guide covers the production Compose profile and Windows endpoint agent installation.

## Configuration and security

- Copy `.env.example` to `.env` for backend settings and replace example secrets before deployment.
- Keep `.env` and provider API keys out of Git; use the deployment platform's environment-variable settings for hosted services.
- Do not use demo or default credentials in a production environment.
- Restrict CORS origins and enable HTTPS for production deployments.

## License

No license is currently specified. Contact the repository owner before reusing or distributing this project.
