# 🚀 SENTINEL AI - LOGIN & STARTUP GUIDE

## 📋 LOGIN CREDENTIALS

```
Username: admin
Password: Admin1234
```

⚠️ **IMPORTANT**: Change this password immediately after first login!

---

## 🌐 ACCESS URLs

| Service | URL | Status |
|---------|-----|--------|
| **Frontend Dashboard** | http://localhost:5173 | Running |
| **Backend API** | http://localhost:8000 | Running |
| **API Documentation** | http://localhost:8000/docs | Available |
| **API Redoc** | http://localhost:8000/redoc | Available |

---

## 🔄 STARTUP INSTRUCTIONS

### Option 1: Using Docker Compose (Recommended)

```bash
# Navigate to project directory
cd "C:\Users\Administrator\Desktop\Sentinel AI"

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Option 2: Manual Local Start

#### Terminal 1 - Start Backend
```bash
cd "C:\Users\Administrator\Desktop\Sentinel AI\backend"

# Initialize database (first time only)
python init_db.py

# Start FastAPI server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

#### Terminal 2 - Start Frontend
```bash
cd "C:\Users\Administrator\Desktop\Sentinel AI\frontend"

# Install dependencies (first time only)
npm install

# Start development server
npm run dev
```

---

## 📝 FIRST LOGIN

1. **Open Browser**: http://localhost:5173
2. **Enter Credentials**:
   - Username: `admin`
   - Password: `Admin1234`
3. **Click Login**
4. **Redirect**: Should go to dashboard

---

## ✅ VERIFY BACKEND IS WORKING

Check API health:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "sentinel-api",
  "timestamp": "2026-07-09T..."
}
```

Test login:
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin1234"}'
```

Expected response:
```json
{
  "success": true,
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": {
    "username": "admin",
    "email": "admin@sentinelai.local",
    "role": "Admin"
  }
}
```

---

## 🔧 TROUBLESHOOTING

### Backend Won't Start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process using port 8000
taskkill /PID <PID> /F

# Try again
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend Won't Start
```bash
# Clear npm cache
npm cache clean --force

# Reinstall dependencies
rm -r node_modules package-lock.json
npm install

# Start again
npm run dev
```

### Database Issues
```bash
# Reset database (DELETE ALL DATA)
del sentinel.db

# Reinitialize
python init_db.py
```

### Port Conflicts
- **Frontend**: Default port 5173, can change in `vite.config.js`
- **Backend**: Default port 8000, change with `--port` flag
- **Database**: SQLite uses local file, no port needed

---

## 🎯 DASHBOARD FEATURES

After login, you'll see:

### 📊 Summary Cards
- Total Employees
- Total Devices
- Total Incidents
- System Status

### 👥 Employee Management
- View all employees
- Add new employee
- Edit employee info
- Delete employee
- Risk scoring

### 💻 Device Management
- View all devices
- Register new device
- Edit device info
- Delete device
- Real-time metrics (CPU/RAM/Disk)

### 🔗 Device Assignment
- Assign device to employee
- View assignments
- Track assignment dates

### ⚠️ Incident Management
- View security incidents
- Filter by severity
- Track incident status
- View recommendations

### 🎯 Event Reporting
- Report security events
- Select event type
- Set severity level
- Add description

### ⚙️ Settings
- Change password
- Security policies
- System configuration

---

## 🔐 SECURITY NOTES

1. **Change Default Password**: Do this immediately!
   - Settings → Change Password
   - Enter current: `Admin1234`
   - Enter new password (8+ chars)
   - Confirm new password

2. **Enable HTTPS in Production**: Currently using HTTP

3. **Backup Database**: Located at `./backend/sentinel.db`

4. **Keep Logs**: Stored in `./backend/logs/`

---

## 📞 SUPPORT

If you encounter issues:

1. **Check Backend Logs**
   ```bash
   # If running locally
   Check Terminal 1 for errors
   
   # If using Docker
   docker-compose logs backend
   ```

2. **Check Frontend Logs**
   ```bash
   # Browser Developer Tools
   Press F12 → Console tab
   Look for errors in red
   ```

3. **API Documentation**
   - Visit: http://localhost:8000/docs
   - Try endpoints directly in Swagger UI

---

## 🚀 NEXT STEPS

1. ✅ Login to dashboard
2. ✅ Add test employees
3. ✅ Register test devices
4. ✅ Assign devices to employees
5. ✅ Report test security events
6. ✅ View incidents generated
7. ✅ Change password for security
8. ✅ Configure security policies

---

**Status**: ✅ **READY TO USE**

**Version**: 1.0.0

**Last Updated**: 2026-07-09
