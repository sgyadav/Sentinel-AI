# Sentinel AI Office Deployment

This deployment profile is for an internal company or office LAN:

- One central Sentinel server runs the dashboard, API, WebSocket service, and database.
- Office endpoint PCs run the endpoint agent.
- Users open the SOC dashboard in a browser at `http://SERVER_IP/`.

## 1. Prepare The Server

Install Docker Desktop or Docker Engine on the server.

Copy `.env.example` to `.env` in the project root. Set a random `SECRET_KEY` of at least 32 characters and set `SENTINEL_INITIAL_ADMIN_PASSWORD` before first startup. Keep `.env` private and do not commit it.

```powershell
Copy-Item .env.example .env
notepad .env
```

For example, generate a JWT secret with Python:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Set `SENTINEL_CORS_ORIGINS` to the browser origin(s) that will open the dashboard. If the dashboard should run on a different port, change:

```env
SENTINEL_HTTP_PORT=80
```

Allow inbound traffic to that port in Windows Firewall or your server firewall.

## 2. Launch The Application

From the project root:

```powershell
docker compose -f docker-compose.prod.yml up -d --build
```

Check service status:

```powershell
docker compose -f docker-compose.prod.yml ps
```

Check backend health through the frontend proxy:

```powershell
Invoke-WebRequest http://127.0.0.1/api/health -UseBasicParsing
```

Open the dashboard:

```text
http://SERVER_IP/
```

Use the sidebar page `Endpoint Monitoring` for the real-time view.

## 3. Install Endpoint Agent On Windows PCs

Run PowerShell as Administrator on each endpoint PC.

Copy the project folder, or at least the `agent` and `deployment` folders, to the PC. In the Render backend environment, set `SENTINEL_AGENT_TOKEN` to a separate random value of at least 32 characters. Then run this from an elevated PowerShell prompt:

```powershell
powershell -ExecutionPolicy Bypass -File .\deployment\install-agent-windows.ps1 -ServerUrl "https://your-service.onrender.com"
```

The installer securely prompts for the backend's `SENTINEL_AGENT_TOKEN`, saves it in `C:\ProgramData\SentinelAI\config.json` with access limited to SYSTEM and Administrators, and schedules the full endpoint agent. Use the backend origin only; the agent appends its telemetry routes. For a LAN server, use its HTTPS origin when available. The same shared token must be entered on each agent and rotated on all agents when changed.

The script:

- installs Python dependencies from `agent/requirements.txt`;
- creates a Windows Scheduled Task named `Sentinel Endpoint Agent`;
- starts the agent automatically at boot;
- sends authenticated heartbeats, process snapshots, USB events, and Windows session events to the backend.

To remove the agent:

```powershell
powershell -ExecutionPolicy Bypass -File .\deployment\uninstall-agent-windows.ps1
```

## 4. Verify Real-Time Monitoring

1. Open `http://SERVER_IP/`.
2. Go to `Endpoint Monitoring`.
3. Confirm the endpoint hostname appears.
4. Confirm CPU, RAM, disk, process, network, and event data update.
5. Open `Devices`, `Dashboard`, and `Incidents` to verify the SOC views are receiving live data.

## 5. Go-Live Checklist

Before using this outside a trusted LAN:

- Put the dashboard behind HTTPS.
- Keep `SECRET_KEY`, `SENTINEL_AGENT_TOKEN`, and `SENTINEL_INITIAL_ADMIN_PASSWORD` out of Git. Rotate the initial admin password after first login.
- Use a different value for `SECRET_KEY` and `SENTINEL_AGENT_TOKEN`; never use the admin JWT key as the agent credential.
- Configure regular backups of the Docker volume `sentinel_data`.
- Add API keys for threat-intelligence providers if those pages are used.
- Decide who can close incidents and who can run endpoint response actions.
- Keep endpoint firewall rules and antivirus exclusions documented.

## Useful Commands

View logs:

```powershell
docker compose -f docker-compose.prod.yml logs -f
```

Restart services:

```powershell
docker compose -f docker-compose.prod.yml restart
```

Stop services:

```powershell
docker compose -f docker-compose.prod.yml down
```

Backup the SQLite database volume:

```powershell
docker run --rm -v sentinelai_sentinel_data:/data -v ${PWD}:/backup alpine cp /data/sentinel.db /backup/sentinel-backup.db
```
