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
Set-Location backend
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at `http://127.0.0.1:8000`; interactive API documentation is at `http://127.0.0.1:8000/docs`.

### Frontend

In a second terminal from the repository root:

```powershell
Set-Location frontend
npm ci
npm run dev
```

Vite prints the local dashboard URL when the development server starts.

## Existing hosted deployments

The frontend is the Vite application in `frontend/`, and the backend is deployed separately on Render. Keep the current Vercel project connected to this repository with its existing project settings. If configuring a new Vercel project, use `frontend` as the Root Directory, `npm run build` as the Build Command, and `dist` as the Output Directory.

The frontend currently targets the existing Render API URL in its API client. Backend URL or environment changes should be coordinated with the Vercel project so the deployed dashboard continues to reach its API.

## Container deployment

For the Docker-based office/LAN deployment, see [deployment/README.md](deployment/README.md). That guide covers the production Compose profile and Windows endpoint agent installation.

## Configuration and security

- Copy `.env.example` to `.env` for backend settings and replace example secrets before deployment.
- Keep `.env` and provider API keys out of Git; use the deployment platform's environment-variable settings for hosted services.
- Do not use demo or default credentials in a production environment.
- Restrict CORS origins and enable HTTPS for production deployments.

## License

No license is currently specified. Contact the repository owner before reusing or distributing this project.
