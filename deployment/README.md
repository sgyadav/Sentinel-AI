# Sentinel AI Office Deployment

This deployment profile is for an internal company or office LAN:

- One central Sentinel server runs the dashboard, API, WebSocket service, and database.
- Office endpoint PCs run the endpoint agent.
- Users open the SOC dashboard in a browser at `http://SERVER_IP/`.

## 1. Prepare The Server

Install Docker Desktop or Docker Engine on the server.

Copy `.env.example` to `.env` in the project root and edit it:

```powershell
Copy-Item .env.example .env
notepad .env
```

For a first LAN deployment, the defaults are enough. If the dashboard should run on a different port, change:

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

Copy the project folder, or at least the `endpoint_agent` and `deployment` folders, to the PC. Then run:

```powershell
powershell -ExecutionPolicy Bypass -File .\deployment\install-agent-windows.ps1 -ServerUrl "http://SERVER_IP/api/agent/status"
```

Replace `SERVER_IP` with the IP or DNS name of the Sentinel server.

The script:

- installs Python dependencies from `endpoint_agent/requirements.txt`;
- creates a Windows Scheduled Task named `Sentinel Endpoint Agent`;
- starts the agent automatically at boot;
- posts real telemetry to the central server.

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
- Replace demo login behavior with enforced authentication and roles.
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
