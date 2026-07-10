# ⚡ QUICK START GUIDE

## 🚀 5-Minute Setup

### Prerequisites
- Docker & Docker Compose installed
- Port 5173 & 8000 available

### Step 1: Start Application
```bash
cd sentinel-ai
docker-compose up -d
```

### Step 2: Wait for Services
```bash
docker-compose ps
# Wait until both show "Up"
```

### Step 3: Access Dashboard
Open browser: **http://localhost:5173**

### Step 4: Login
```
Username: admin
Password: SecurePass123
```

### Step 5: View Dashboard
Dashboard loads with:
- Employee metrics
- Device status
- Threat statistics
- Recent incidents

---

## 📊 Dashboard Features

| Feature | Location | Description |
|---------|----------|-------------|
| Employee Count | Top-left card | Total registered employees |
| Device Count | Top-2nd card | Total devices managed |
| Incidents | Top-3rd card | Security incidents logged |
| Open Issues | Top-4th card | Active investigations |
| Threat Chart | Bottom-left | Severity breakdown (24h) |
| Device Status | Bottom-right | Online vs Offline count |
| Threats Feed | Bottom | Recent threats timeline |

---

## 🔑 API Access

### Get Auth Token
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"SecurePass123"}'
```

Response:
```json
{
  "success": true,
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "email": "admin@example.com",
    "role": "Admin"
  }
}
```

### Use Token in Requests
```bash
curl -H "Authorization: Bearer eyJhbGc..." \
  http://localhost:8000/api/realtime/dashboard/overview
```

---

## 📝 Common Tasks

### Register New Employee
```bash
curl -X POST http://localhost:8000/employees \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "employee_id": "EMP-002",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "department": "Security",
    "designation": "Security Officer"
  }'
```

### Register Device
```bash
curl -X POST http://localhost:8000/devices \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "PC-002",
    "ip_address": "192.168.1.101",
    "operating_system": "Windows 11"
  }'
```

### Report Security Event
```bash
curl -X POST http://localhost:8000/event \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "PC-001",
    "event_type": "Malware",
    "severity": "Critical",
    "description": "Ransomware detected in user directory"
  }'
```

### Get Dashboard Data
```bash
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/realtime/dashboard/overview
```

---

## 🌐 WebSocket Connection

Connect to real-time updates:

```javascript
// In browser console or Node.js
const token = localStorage.getItem('token');
const ws = new WebSocket('ws://localhost:8000/ws/dashboard/client-1');

ws.onopen = () => {
  console.log('Connected');
  ws.send('ping');
};

ws.onmessage = (event) => {
  console.log('Message:', JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error('Error:', error);
};
```

---

## 🧪 Test Scenarios

### Test 1: Complete Flow
1. Login with admin credentials
2. View dashboard
3. Create new employee
4. Register device
5. Assign device to employee
6. Report security event
7. View incident in dashboard

### Test 2: Authentication
1. Try login with wrong password → Should fail
2. Try 5 times → Account should lock
3. Wait 30 minutes → Account unlocks

### Test 3: Real-time Updates
1. Open dashboard in 2 browser windows
2. Report event in one window
3. Should appear in other window (10s max)

---

## 🔍 Troubleshooting

### Frontend Not Loading
```bash
# Check frontend status
docker-compose logs frontend

# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose restart frontend
```

### Backend Not Responding
```bash
# Check backend status
docker-compose logs backend

# Check if healthy
curl http://localhost:8000/health

# Restart backend
docker-compose restart backend
```

### Database Issues
```bash
# Stop all
docker-compose down -v

# Start fresh
docker-compose up -d
```

---

## 📚 Documentation

- **Full Docs**: README.md
- **Deployment**: DEPLOYMENT_READY.md
- **GitHub Setup**: GITHUB_DEPLOYMENT.md
- **Implementation**: IMPLEMENTATION_SUMMARY.md
- **Frontend Fix**: FRONTEND_FIX_SUMMARY.md

---

## 🚀 Production Deployment

1. Update `.env` with production values
2. Switch to PostgreSQL
3. Set DEBUG=False
4. Configure CORS_ORIGINS
5. Deploy to cloud (AWS/GCP/Azure)

See DEPLOYMENT_READY.md for details.

---

## 🤝 Contributing

1. Fork repository
2. Create feature branch
3. Make changes
4. Test locally
5. Submit pull request

---

## 📞 Support

- **Issues**: GitHub Issues
- **API Docs**: http://localhost:8000/api/docs
- **Discussions**: GitHub Discussions

---

## ✅ Checklist

- [ ] Docker Compose running
- [ ] Frontend accessible (http://localhost:5173)
- [ ] Backend accessible (http://localhost:8000)
- [ ] Can login with admin credentials
- [ ] Dashboard loads with data
- [ ] Can create employees
- [ ] Can register devices
- [ ] Can report events
- [ ] API working correctly
- [ ] WebSocket connecting

---

**Ready to go!** 🎉

Visit http://localhost:5173 and start monitoring threats in real-time.
