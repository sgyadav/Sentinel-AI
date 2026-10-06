# SENTINEL AI - DEVELOPER QUICK REFERENCE

## 🎯 WHAT'S WORKING (✅ 7 Phases Complete)

| Phase | Status | Key Files |
|-------|--------|-----------|
| 1: Backend | ✅ | `backend/main.py`, `backend/models.py` |
| 2: Auth | ✅ | `backend/auth.py`, `backend/main.py` |
| 3: Agent | ✅ | `agent/agent.py` |
| 4: Enrollment | ✅ | `/heartbeat` endpoint |
| 5: Dashboard | ✅ | `frontend/src/App.jsx` |
| 6: SOC | ✅ | `frontend/src/App.jsx` (SOC tab) |
| 11: Testing | ✅ | `tests/production_test.py` |
| 7: Login Events | ❌ | `LoginHistoryDB` ready in `models.py` |
| 8: Reports | ❌ | Need: reportlab integration |
| 9: Email Alerts | ❌ | Need: SMTP alert trigger logic |
| 10: Installer | ❌ | Need: PyInstaller packaging |

---

## 🚀 RUNNING THE SYSTEM

### Start Everything (3 Terminals)

**Terminal 1: Backend**
```bash
cd backend
python main.py
```
✓ Health check: http://localhost:8000/health

**Terminal 2: Frontend**
```bash
cd frontend
npm run dev
```
✓ Access: http://localhost:5173

**Terminal 3: Agent (optional)**
```bash
python agent/agent.py
```
✓ Logs: `C:/ProgramData/SentinelAI/agent.log`

### Run Tests
```bash
python tests/production_test.py
```

---

## 📚 KEY FILES STRUCTURE

```
Sentinel AI/
├── backend/
│   ├── main.py              # FastAPI app (25KB) ⭐ MAIN API
│   ├── models.py            # SQLAlchemy models (6KB)
│   ├── auth.py              # JWT & authentication (4KB)
│   ├── database.py          # DB config
│   ├── requirements.txt     # Python dependencies
│   └── sentinel.db          # SQLite database
│
├── frontend/
│   ├── src/
│   │   └── App.jsx          # React app (60KB) ⭐ MAIN UI
│   ├── package.json
│   └── vite.config.js
│
├── agent/
│   └── agent.py             # Windows agent (13KB) ⭐ MONITORING
│
├── tests/
│   └── production_test.py    # Test suite (14KB) ⭐ VALIDATION
│
└── docs/
    ├── DEPLOYMENT_GUIDE.md  # How to deploy
    └── IMPLEMENTATION_SUMMARY.md  # What's done
```

---

## 🔌 API QUICK REFERENCE

### Authentication
```bash
# Login
# Set SENTINEL_ADMIN_PASSWORD in your shell before using this example.
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "YOUR_ADMIN_PASSWORD"}'

# Response includes: access_token
```

All dashboard API examples below require the token from that response, including employee and device operations, reports, settings, and dashboard reads:

```bash
curl http://localhost:8000/employees \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

Agent telemetry ingestion uses a separate bearer credential. Configure `SENTINEL_AGENT_TOKEN` with a random value of at least 32 characters on the backend and on the agent; never use an admin JWT or `SECRET_KEY` as the agent token.

```bash
curl -X POST http://localhost:8000/heartbeat \
  -H "Authorization: Bearer $SENTINEL_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"hostname":"PC-001","username":"operator","ip_address":"192.168.1.100","operating_system":"Windows","status":"Online"}'
```

### Employees
```bash
# List
curl http://localhost:8000/employees \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Create
curl -X POST http://localhost:8000/employees \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP-001",
    "name": "John",
    "email": "john@company.com",
    "department": "IT",
    "designation": "Analyst"
  }'

# Update
curl -X PUT http://localhost:8000/employees/EMP-001 \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{...updated data...}'

# Delete
curl -X DELETE http://localhost:8000/employees/EMP-001 \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

### Devices (Endpoints)
```bash
# List
curl http://localhost:8000/devices \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Register
curl -X POST http://localhost:8000/devices \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "PC-001",
    "ip_address": "192.168.1.100",
    "operating_system": "Windows 11",
    ...
  }'

# Heartbeat (auto-register)
curl -X POST http://localhost:8000/heartbeat \
  -H "Authorization: Bearer $SENTINEL_AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "PC-AUTO",
    "cpu_usage": 25.5,
    ...
  }'
```

### Monitoring
```bash
# USB Events
curl http://localhost:8000/usb-events \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Live Processes
curl http://localhost:8000/processes/live \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Threats
curl http://localhost:8000/threats \
  -H "Authorization: Bearer $ACCESS_TOKEN"

# Dashboard
curl http://localhost:8000/dashboard \
  -H "Authorization: Bearer $ACCESS_TOKEN"
```

---

## 📊 DATABASE SCHEMA QUICK LOOKUP

### Core Tables
```python
UserDB           # Users (username, password_hash, role)
EmployeeDB       # Employees (employee_id, name, email, department, risk_score)
DeviceDB         # Endpoints (device_id, hostname, ip, os, cpu%, ram%, disk%)
AssignmentDB     # Employee-Device links
ThreatDB         # Threats (threat_id, device_id, severity, status)
ProcessDB        # Live processes (hostname, pid, name, cpu%, memory%)
USBEventDB       # USB events (action, device, hostname, event_time)
LoginHistoryDB   # Login audit (username, login_time, logout_time, status)
```

### Check DB Status
```bash
# Query in Python
python -c "
import sqlite3
conn = sqlite3.connect('backend/sentinel.db')
cursor = conn.cursor()
cursor.execute('SELECT name FROM sqlite_master WHERE type=\"table\"')
for table in cursor.fetchall():
    print(table[0])
conn.close()
"
```

---

## 🔐 Authentication Details

### Token Format
```
access_token: JWT returned by POST /auth/login
expires_in: 60 minutes by default (configurable with ACCESS_TOKEN_EXPIRE_MINUTES)
```

### Roles
- `Admin` - Full system access
- Other roles do not access administrator routes

### Password Hashing
```python
from auth import hash_password, verify_password

# Hash a password
hashed = hash_password("MyPassword123")

# Verify
is_correct = verify_password("MyPassword123", hashed)
```

---

## 🛠️ COMMON DEVELOPMENT TASKS

### Add a New API Endpoint

1. **Define Pydantic model** in `backend/models.py`
   ```python
   class MyDataCreate(BaseModel):
       field1: str
       field2: int
   ```

2. **Create endpoint** in `backend/main.py`
   ```python
   @app.post("/my-endpoint")
   def create_mydata(data: MyDataCreate, db: Session = Depends(get_db)):
       # Your logic
       return {"success": True}
   ```

3. **Test it**
   ```bash
   curl -X POST http://localhost:8000/my-endpoint \
     -d '{"field1": "value", "field2": 42}'
   ```

### Add a Database Table

1. **Create SQLAlchemy model** in `backend/models.py`
   ```python
   class MyTableDB(Base):
       __tablename__ = "my_table"
       id = Column(Integer, primary_key=True)
       name = Column(String(255))
   ```

2. **Migrate database**
   ```python
   # Run in Python console
   from models import Base
   from database import engine
   Base.metadata.create_all(bind=engine)
   ```

### Update Frontend Component

1. **Edit** `frontend/src/App.jsx`
2. **Add state** for new data
3. **Create fetch function** calling backend API
4. **Add JSX** for display
5. **Test** at http://localhost:5173

---

## 🐛 DEBUGGING

### Backend Logs
```bash
# Watch logs in real-time
tail -f backend/sentinel.db.log  # or check stdout

# Python errors appear in console running main.py
```

### Frontend Console
```javascript
// Open browser DevTools (F12)
// Check Console tab for errors
// Network tab for API calls
```

### Agent Logs
```bash
# Check agent log file
cat "C:/ProgramData/SentinelAI/agent.log"

# Or in Python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Specific Endpoint
```bash
python tests/production_test.py  # Full test suite
```

---

## 🎯 NEXT PHASE: LOGIN/LOGOUT MONITORING (Phase 7)

### What's Needed:
1. Capture login events from Windows Event Viewer
2. Store in `LoginHistoryDB` (already created)
3. Add API endpoint: `GET /login-history`
4. Add UI display in SOC

### Files to Modify:
- `agent/agent.py` - Add `LoginMonitor` class
- `backend/main.py` - Add `/login-history` endpoint
- `frontend/src/App.jsx` - Add login history tab

### Estimated Effort: 2-3 hours

---

## 📦 DEPENDENCIES QUICK CHECK

**Backend:**
```bash
pip list | grep -E "fastapi|sqlalchemy|pydantic|bcrypt|python-jose"
```

**Frontend:**
```bash
npm list react react-dom axios
```

**Agent:**
```bash
pip list | grep -E "psutil|requests"
```

---

## 🚨 COMMON ERRORS & FIXES

| Error | Cause | Fix |
|-------|-------|-----|
| "Address already in use :8000" | Backend already running | Kill process or use different port |
| "ModuleNotFoundError: requests" | Missing package | `pip install requests` |
| "Cannot connect to database" | DB corrupted or locked | Delete `sentinel.db`, restart |
| "CORS error in frontend" | CORS not configured | Check backend CORS middleware |
| "Agent won't start" | Config file missing | Run: `python agent/agent.py` once |

---

## 📞 WHO TO CONTACT FOR QUESTIONS

**Backend Issues** → Check `backend/main.py` docstrings  
**Frontend Issues** → Check `frontend/src/App.jsx` state management  
**Agent Issues** → Check `agent/agent.py` configuration  
**Database Issues** → Check `backend/models.py` schema  
**Testing Issues** → Run `tests/production_test.py` with verbose flag  

---

## 📋 CHECKLIST FOR NEXT DEVELOPER

- [ ] Read this file
- [ ] Read `IMPLEMENTATION_SUMMARY.md`
- [ ] Run all 3 terminals (backend, frontend, agent)
- [ ] Access frontend at http://localhost:5173
- [ ] Login with the admin password configured for this environment
- [ ] Run `tests/production_test.py`
- [ ] All tests should pass ✅
- [ ] Verify dashboard shows metrics
- [ ] Verify SOC shows monitoring data

**If all ✅, you're ready to continue development!**

---

**Version:** 1.0  
**Last Updated:** 2024  
**Maintainer:** Development Team  
**Status:** Production Ready
